import subprocess

def option1():
    print("Customer onboarding - option 1...")
    subprocess.run(["python", "customeronboarding.py"])
    # code to run for option 1 here

def option2():
    print("Credit account - option 2...")
    subprocess.run(["python", "customercredit.py"])

def option3():
    print("Addon plan activation - option 3...")
    subprocess.run(["python", "customeraddonactivation.py"])

def option4():
    print("Customer deactivation - Option 4...")
    subprocess.run(["python", "customerdeactivation.py"])

def option5():
    print("Voice on net call - Option 5...")
    subprocess.run(["python", "VoiceonnetGenerator.py"])

def option6():
    print("Voice offnet call - Option 6...")
    subprocess.run(["python", "VoiceoffnetGenerator.py"])

def option7():
    print("Voice ISD call - Option 7...")
    subprocess.run(["python", "VoiceISDGenerator.py"])

def option8():
    print("SMS on net event - Option 8...")
    subprocess.run(["python", "SMSonnetGenerator.py"])

def option9():
    print("SMS off net event - Option 9...")
    subprocess.run(["python", "SMSoffnetGenerator.py"])

def option10():
    print("SMS ISD event - Option 10...")
    subprocess.run(["python", "SMSISDGenerator.py"])

def option11():
    print("Data session - Option 11...")
    subprocess.run(["python", "DataGenerator.py"])


def main():
    while True:
        print("Please select an option:")
        print("1) Customer registration - 1")
        print("2) Credit account - 2")
        print("3) Add on plan activation - 3")
        print("4) Cusromer deactivation  - 4")
        print("5) Voice call - 5")
        print("6) SMS event - 6")
        print("7) Data event - 7")
        print("8) Exit - 8")

        choice = input("Enter your selection: ")
        if choice == "1":
            option1()
        elif choice == "2":
            option2()
        elif choice == "3":
            option3()
        elif choice == "4":
            option4()
        elif choice == "5":
            print("Voice on net call - 1")
            print("Voice off net call - 2")
            print("Voice ISD call - 3")
            choice = input("Enter your selection: ")
            if choice == "1":
                option5()
            elif choice == "2":
                option6()
            elif choice == "3":
                option7()
            else:
                print("Exiting ...")
                break
        elif choice == "6":
            print("SMS on net event - 1")
            print("SMS off net event - 2")
            print("SMS ISD event - 3")
            choice = input("Enter your selection: ")
            if choice == "1":
                option8()
            elif choice == "2":
                option9()
            elif choice == "3":
                option10()
            else:
                print("Exiting ...")
                break
        elif choice == "7":
            option11()
        elif choice == "8":
            break
        else:
            print("Invalid selection. Please try again.")
            break

if __name__ == "__main__":
    main()

