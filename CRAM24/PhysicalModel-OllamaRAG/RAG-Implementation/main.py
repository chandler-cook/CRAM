from localrag import localrag

if __name__ == "__main__":
    # Directly set the file path
    path = "user_input.txt"
    
    # Call the localrag function with the specified path and print the returned score
    score = localrag(path)
    if score is not None:
        print(score)
    else:
        print("No valid score could be calculated.")
