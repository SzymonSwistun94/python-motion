import cv2
import numpy as np
import datetime as dt
import email_utils as email
import string
import random
import os
import os.path as op
import copy

cap = cv2.VideoCapture(0)
THRESHOLD = 0.0001
PIXEL_COUNT = cap.get(cv2.CAP_PROP_FRAME_WIDTH) * cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
PIXEL_THRESHOLD = THRESHOLD * PIXEL_COUNT

GMAIL_LOGIN = "embedded1sys"
GMAIL_PASSWD = "abcd1@34"

EMAIL_DELAY = 120
DESC_EMAIL = "embedded1sys@gmail.com"

KERNEL_DIM = 15


def process_image(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(img, (25, 25), 0)


def rand_string(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))


def send_email(address, msg, img=None):
    global con
    try:
        con
    except:
        con = email.EmailConnection('smtp.gmail.com', GMAIL_LOGIN, GMAIL_PASSWD)

    if img is not None:
        name = rand_string(16) + ".png"
        while op.isfile(name):
            name = rand_string(16) + ".png"

        cv2.imwrite(name, img)
        mail = email.Email(
            from_=GMAIL_LOGIN + "@gmail.com",
            to=address,
            subject="Motion",
            message=msg,
            attachments=[name]
        )
    else:
        mail = email.Email(
            from_=GMAIL_LOGIN + "@gmail.com",
            to=DESC_EMAIL,
            subject="Motion",
            message=msg
        )

    con.send(mail)

    try:
        os.remove(name)
    except:
        pass


def main():
    background_subtractor = cv2.createBackgroundSubtractorMOG2()
    kernel = np.ones((KERNEL_DIM, KERNEL_DIM), np.uint8)

    while True:
        _, frame = cap.read()

        cpy = copy.deepcopy(frame)
        frame = process_image(frame)

        res = background_subtractor.apply(frame)

        _, res = cv2.threshold(res, 25, 100, type=cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # arr = np.array(res)
        non_zero = np.count_nonzero(res)

        # res = cv2.morphologyEx(res, cv2.MORPH_OPEN, kernel)
        res = cv2.dilate(res, kernel)
        res, contours, hierarchy = cv2.findContours(res, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        # contours = np.reshape(contours[0], -1, 2)

        # for i in contours[0]:
        #     print(i)

        if len(contours) > 0:
            for arr in contours:
                for r in arr:
                    x, y = r[0]
                    cv2.circle(cpy, (x, y), 1, (255, 0, 0))

        if non_zero > PIXEL_THRESHOLD:
            # print("Motion")

            global last_mail

            try:
                last_mail
            except:
                last_mail = dt.datetime.fromtimestamp(dt.datetime.now().second + EMAIL_DELAY - 1)
                # send_email(DESC_EMAIL, "Motion spotted", cpy)
                # print "Email sent"
            else:
                if (dt.datetime.now() - last_mail).seconds > EMAIL_DELAY:
                    send_email(DESC_EMAIL, "Motion spotted", cpy)
                    last_mail = dt.datetime.now()
                    print "Email sent"

            pass

        # Display the resulting frame
        cv2.imshow('frame', cpy)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


main()
