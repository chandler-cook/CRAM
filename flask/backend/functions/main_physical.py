from physical_model import physical_model

if __name__ == "__main__":
    # Directly set the file path
    path = "user_input.txt"
    
    # Call the localrag function with the specified path and print the returned score
    score = physical_model(path)
    if score is not None:
        print(score)
    else:
        print("No valid score could be calculated.")

