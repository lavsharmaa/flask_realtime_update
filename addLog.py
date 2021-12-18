while True:
    file1 = open("text.txt", "a")  # append mode
    userInput = input()
    if userInput == 'end':
        file1.close()
        break
    else:
        file1.write(userInput+"\n")
    file1.close()