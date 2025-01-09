


class ChannelTextfield:
    def __init__(self, allowed_width, allowed_channels) -> None:
        self.allowed_width = allowed_width
        self.allowed_channels = allowed_channels

    def decode_input(self, input):
        # try to find out if user input is correct.
        # for this each element must eighter be separated by a comma or a new line character
        # check if user used '.' or ';' to separate channels and replace with ','
        input = input.replace(';', ',')
        input = input.replace('.', ',')
        input = input.replace(' ,', ',')
        input = input.replace(', ', ',')
        for i in range(len(input)):
            # print(input[i:i+1])
            if input[i:i+1] == '\n': # '\n' counts as a single character!
                if input[i-1] != ',':
                    input = input.replace('\n', ',',1) # if user used linebreak and no ','
        return input
    
    def correct_channels_input(self, input):
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
                else:
                    print(f'The channel [{channel}] is not recognized! Proceeding anyways.')
                    # if the channel is not in the allowed channels list it is either misspelled or some user specific name
                    # this is allowed but the user should be notified
                    corrected_input.append(channel)
        corrected_input = ','.join(corrected_input)
        return corrected_input

    def encode_input(self, list_input):
        # reverse to decode, add '\n' after ',' if line would be longer than text widget width
        # todo, for now arbitrary:
        text_width = 3 # in units of channels, so 3 channels per line are allowed, later adapt to actual width of widget
        # remove '\n' characters
        # input = input.replace('\n', '')
        # convert input to list
        # list_input = input.split(',')
        encoded_input = ''
        '''if len(input) > text_width:
            for i in range(len(list_input)):
                if i == 0:
                    encoded_input += list_input[i]
                elif i % text_width == 0:
                    encoded_input += ',' + '\n' + list_input[i]
                else:
                    encoded_input += ',' + list_input[i]'''
        # alternative:
        lines = []
        line = []
        for channel in list_input:
            # only append channel to line if combined length is lower than allowed width
            if sum(len(i) for i in line) + len(channel) > self.allowed_width:
                lines.append(line)
                line = [channel]
            else: 
                line.append(channel)
        lines.append(line) # dont forget about the last unfinished line
        lines = [','.join(line) for line in lines] # join indivicual channels per line with ','
        encoded_input = '\n'.join(lines) # join individual lines with '\n
        return encoded_input