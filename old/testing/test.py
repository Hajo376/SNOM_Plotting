# liste = [0]
# for i in range(5):
#     liste.append(i)
# print(liste)

import tkinter as tk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *



class Example:
    def __init__(self, root) -> None:
        self.root = root
        self.Interface()
        self.allowed_channels = ['O1A','O2A','O3A','O4A','O5A','O1P','O2P','O3P','O4P','O5P']

    def Interface(self):
        self.textfield = ttkb.Text(self.root)
        self.textfield.pack()
        test_text = 'O1A,O2A\nO3A,\nO1P.O1a;O2P ,O3P, O4P'
        self.textfield.insert(END, test_text)
        self.print_button = ttkb.Button(self.root, text='Print Text input', bootstyle=SUCCESS, command=self.Print_Input)
        self.print_button.pack()

    def _Decode_Input(self, input):
        # try to find out if user input is correct.
        # for this each element must eighter be separated by a comma or a new line character
        # check if user used '.' or ';' to separate channels and replace with ','
        input = input.replace(';', ',')
        input = input.replace('.', ',')
        input = input.replace(' ,', ',')
        input = input.replace(', ', ',')
        for i in range(len(input)):
            print(input[i:i+1])
            if input[i:i+1] == '\n': # '\n' counts as a single character!
                if input[i-1] != ',':
                    input = input.replace('\n', ',',1) # if user used linebreak and no ','
        return input
    
    def _Correct_Channels_Input(self, input):
        input = input.replace('\n', '')
        input = input.split(',')
        corrected_input = []
        lower_allowed_channels = [x.lower() for x in self.allowed_channels]
        for channel in input:
            if channel in self.allowed_channels:
                corrected_input.append(channel)
            else:
                if channel.lower() in lower_allowed_channels:
                    index = lower_allowed_channels.index(channel.lower())
                    corrected_input.append(self.allowed_channels[index])
        corrected_input = ','.join(corrected_input)
        return corrected_input


    
    def _Encode_Input(self, input):
        # reverse to decode, add '\n' after ',' if line would be longer than text widget width
        # todo, for now arbitrary:
        text_width = 3 # in units of channels, so 3 channels per line are allowed, later adapt to actual width of widget
        # remove '\n' characters
        input = input.replace('\n', '')
        # convert input to list
        list_input = input.split(',')
        encoded_input = ''
        # print('list input: ', list_input)
        if len(input) > text_width:
            for i in range(len(list_input)):
                if i == 0:
                    encoded_input += list_input[i]
                elif i % text_width == 0:
                    encoded_input += ',' + '\n' + list_input[i]
                else:
                    encoded_input += ',' + list_input[i]
        return encoded_input

    def Print_Input(self):
        text = self.textfield.get('1.0', 'end-1c') # start in the first line at the '0' character and read uttil end but not the last element, since that is a newline character
        print('You entered: [' + text + ']')
        decoded_text = self._Decode_Input(text)
        print('The adjusted text is: [' + decoded_text + ']')
        corrected_text = self._Correct_Channels_Input(decoded_text)
        print('The corrected channels are: ' + corrected_text)
        encoded_text = self._Encode_Input(corrected_text)
        print('The encoded text is: [' + encoded_text + ']')
        self.textfield.delete('0.0', END)
        # self.textfield.delete(0, END)
        self.textfield.tag_config('center', justify=CENTER)
        self.textfield.insert(END, encoded_text, 'center')



# def main(root):
#     textfield = ttkb.Text(root)
#     textfield.pack()
    # print_button = ttkb.Button(root, text='Print Text input', bootstyle=SUCCESS, command=)



if __name__ == "__main__":
    root=tk.Tk()
    # Example(root).pack(side="top", fill="both", expand=True)
    # main(root)
    Example(root)
    root.mainloop()