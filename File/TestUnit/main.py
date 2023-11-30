import logging
import string


def send_log(text, place):
    logging.basicConfig(filename='temp.log', encoding='utf-8', level=logging.INFO,
                        force=True, format='%(asctime)s %(message)s', datefmt='%m-%d %H:%M')
    logging.info("\"" + text + "\"" + " in " + str(place))


def print_info(filename):
    f1 = open('temp.log', 'r+')
    f2 = open(filename, 'a+')
    f2.write(f1.read())
    f1.truncate(0)
    f1.close()
    f2.close()


def send_res(res):
    match res:
        case 'OK':
            filename = 'OK.log'
            print_info(filename)
        case 'ERR':
            filename = 'ERR.log'
            print_info(filename)
        case 'NF':
            filename = 'NF.log'
            print_info(filename)




# for i in range (30):
#     send_log ("Крутое сообщение", i)
#     send_res("NF")