# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 13:17:07 2024
"""

# %% ToDo
# Change in instruction text: Wortlaut der Items
# event.waitKeys() does not wait until button is released

#EDIT

#%%
from psychopy import visual, core, data, gui, logging, event
import os
import pandas as pd
import numpy as np
import sys
import random
from PIL import Image


#%% highPriority() function from Hubert Voogd to make timing in PsychoPy more accurate

import platform

if any(platform.win32_ver()):
    import win32api
    import win32process
    import ctypes


def highPriority():
    if any(platform.win32_ver()):
        winmm = ctypes.WinDLL('winmm')
        winmm.timeBeginPeriod(1)
        win32process.SetPriorityClass(win32api.GetCurrentProcess(), win32process.HIGH_PRIORITY_CLASS)


highPriority()


#%% Classes and functions

# class sliderDataClass:
#     """Class to store the data from the slider. Use .reset() to reset the stored values."""
#
#     def __init__(self):
#         self.questionOrder = []
#         self.questionText = {'imagine': 'How difficult is it for you to imagine that the fruit was hidden behind the occluder?',
#                              'imagine_label': ['very easy', 'easy', 'neither nor', 'difficult', 'very difficult'],
#                              'plausible': 'How likely do you think it is that the fruit was hidden behind the occluder?',
#                              'plausible_label': ['very unlikely', 'unlikely', 'neither nor', 'likely', 'very likely']}
#         self.reset()
#
#     def reset(self):
#         """Reset the slider values."""
#
#         self.imagineRt = None
#         self.imagineRating = None
#         self.plausibleRt = None
#         self.plausibleRating = None
#         self.sliderTime = {'plausible': None, 'imagine': None}
#
#
# sliderData = sliderDataClass()  # RESET after each trial


# def drawSlider(slider_name, mouseObj, screenMessage, respData):
#     """Takes a slider object as input, reveals the mouse and draws the slider on the screen.
#     Adds the response on the slider and the reaction time to respData.
#     """
#
#     mouseObj.setExclusive(False)
#
#     for qLabel in respData.questionOrder:
#
#         # set the slider question
#         screenMessage.text = respData.questionText[qLabel]
#
#         # set slider labels depending on the question
#         # https://discourse.psychopy.org/t/randomise-sliders-with-different-labels/31901/2
#         labelList = respData.questionText[qLabel+'_label']
#         for idx, obj in enumerate(slider_name.labelObjs):
#             obj.text = slider_name.labels[idx] = labelList[idx]
#
#         # respData.sliderTime[qLabel] = expClock.getTime()
#         count = 1
#
#         # From the source code: This resets the rating value of the scale and also resets the clock for the RT
#         slider_name.reset()
#
#         # Loop until participant made a rating
#         while slider_name.getRating() is None:
#             stimulus_occluder.draw()
#             stimulus_scene.draw()
#             screenMessage.draw()
#             slider_name.draw()
#             win.flip()
#
#             if count == 2:  # get the time after the second flip
#                 respData.sliderTime[qLabel] = expClock.getTime()
#             count += 1
#
#         if qLabel == 'imagine':
#             respData.imagineRt = slider_name.getRT()
#             respData.imagineRating = slider_name.getRating()
#         elif qLabel == 'plausible':
#             respData.plausibleRt = slider_name.getRT()
#             respData.plausibleRating = slider_name.getRating()
#
#         core.wait(waitBetweenItems)
#
#     mouseObj.setExclusive(True)


def takeBreak(key_to_wait='space'):
    """Wait for a fixed amount of time, then press space to continue."""

    message.text = 'Break'
    message.draw()
    win.flip()
    
    core.wait(breakTime)
    message.text = 'Press space to continue.'
    message.draw()
    win.flip()

    event.waitKeys(keyList=key_to_wait)


def textMessage(screenText, key_to_wait='space'):
    """Display text message and wait for key press."""

    message.text = screenText
    message.draw()
    win.flip()
    event.waitKeys(keyList=[key_to_wait])  # must be a list otherwise it does not wait for space and accepts any key
    checkQuit()


def checkQuit(check_key='c', mod_key ='ctrl'):
    escapekey = event.getKeys(keyList=[check_key], modifiers=True)

    for key in escapekey:
        if check_key in key:
            for mod in key:
                if mod_key in mod:
                    if mod[mod_key] == True:
                        quitExperiment()


def quitExperiment():
    exp_handler.abort()  # Has to be called, otherwise the experimentHandler tries to save a crash file
    mouse.setExclusive(False)  # Otherwise GUI will freeze on next run
    win.winHandle.set_fullscreen(False)  # Exit full screen because gui has problems with fullscreen.
    win.close()  # Call win.close() because window does not close if only calling core.quit()
    core.quit()


def extract_source(functionName, fileName='source_tmp'):
    """Save to file to inspect source code."""

    import inspect
    with open(fileName+'.txt', 'x') as f:
        f.write(inspect.getsource(functionName))


def getrandpos(df, number_positions=8):
    pairlist = list(set(df['pair'])).copy()

    # Shuffle a list of 8 possible positions and distribute over 6 given positions
    for indx, p in enumerate(pairlist):
        positions = list(range(1,number_positions+1))
        random.shuffle(positions)
        for num in range(1,7):
            pos_tmp = positions.pop()

            df.loc[df.pair == p, 'pos{posnum}_{sce}'.format(posnum=str(num), sce='scene1')] = pos_tmp  # positions.pop()

            # For scene 2: Add same positions only for distractors
            if num > number_targets:
                df.loc[df.pair == p, 'pos{posnum}_{sce}'.format(posnum=str(num),
                                                                sce='scene2')] = pos_tmp  # positions.pop()

    # For scene 2: Swop positions in signal trials, but keep the same as in scene 1 in noise trials
    df['pos1_scene2'] = np.where(df['signal'] == 'signal', df['pos2_scene1'], df['pos1_scene1'])
    df['pos2_scene2'] = np.where(df['signal'] == 'signal', df['pos1_scene1'], df['pos2_scene1'])


# %% Set variables

debug = True
# playInstructions = False

repetitionsExp = 1
repetitionsPractise = 1
num_practise = 10

# {} because we will use .format() for these fields later on
data_folder_path = "../data/sub-{ID}"
data_file_name = data_folder_path+"/sub-{ID}_{dataType}"
instruction_path = "instructions/"
stim_path = '../stimuli/stimuli/'

screenResolution = (1920, 1080)
imageSize = [2,2]#[0.95, 0.95]

ISI_duration = 1.0  # Time in seconds
occluderDuration = 4.0  # Time in seconds
scene1Duration = 1.0  # Time in seconds
scene2Duration = 1.0  # Time in seconds
breakTime = 60.0  # Time in seconds. Duration of the break.
breakTrial = 60  # Number of trials after which to make a break
waitBetweenItems = 0.2  # Seconds

# imagePosOccl = [0, 0]
# imagePosScene = [0, 0]
imagePos = [0, 0]

textHeight = 0.08  # 50
textWrap = 0.8  # 1.5  # 1500

# sliderTicks = (range(5))

font_name = 'Arial'  # Slider has difficulties with some other fonts
continueKey = ['space']
responseKeys = ['left', 'right']
responseKeysRating = [str(num) for num in list(range(1, 5))]

targ_distr_dict = ['target1', 'target2', 'distractor3', 'distractor4', 'distractor5', 'distractor6']
number_targets = 2

if debug == True:
    occluderDuration = 1.0
    breakTime = 1.0

#%%

# GUI (present before defining window, because fullscr prevents interaction with other windows)
# * makes gui fields mandatory
exp_info = {
    'ID*': '',
    'Age*': '',
    'Gender*': ['-- select input --', 'female', 'male', 'diverse']
}

infoDlg = gui.DlgFromDict(exp_info, title='IAWM '+data.getDateStr(), sortKeys=False)
if not infoDlg.OK:  # Stop experiment if participant pressed cancel
    print('Experiment cancelled')
    core.quit()
elif infoDlg.OK == True and '-- select input --' in [exp_info['Gender*']]:  # Check if gender and block order is selected
    raise ValueError('Experiment stopped. Please fill in all fields.')

# Remove * from dictionary keys
for key in list(exp_info.keys()):  # Use list to make a copy of the object
    exp_info[key[0:-1]] = exp_info.pop(key)  # Remove the old key (pop) and replace with new name (key[0:-1])

exp_info['date'] = data.getDateStr()  # Add a date field to dict

# Set presentation order of blocks
expBlocks = ['practise', 'experiment']


os.mkdir(data_folder_path.format(**exp_info))

# Create a clock for the experiment
expClock = core.Clock()

# Create a logfile
logfile = logging.LogFile(data_file_name.format(**exp_info, dataType='logfile')+".log", level=logging.INFO)

logging.setDefaultClock(expClock)  # Make logfile use the same time as the experiment
logging.info('Changed logfile clock to experiment clock (expClock).')

logging.info('Running Python version: {}'.format(sys.version))
# logging.info('Range slider ticks: {}'.format(sliderTicks))

# Create window and keyboard
win = visual.Window(fullscr=True, color='white', size=screenResolution, allowGUI=False, units='norm')

# Get a reference time for the keyboard and the internal clock
exp_tick_ref = expClock.getTime()

screenRefresh = win.getActualFrameRate()

logging.info('Reference time of script (exp_tick_ref): {}'.format(exp_tick_ref))
logging.info('Measured frame rate {}'.format(screenRefresh))

# Current bug with mouse visibility (PsychoPy 2023.2.3)
# Either win.mouseVisible = False with every win.flip() or set mouse.setExclusive(True)
# https://discourse.psychopy.org/t/mouse-still-visible-on-windows-11-psychopy-2023-2-1/36333/3
# https://discourse.psychopy.org/t/mouse-still-visible-on-windows-11-psychopy-2023-2-1/36333/4
mouse = event.Mouse()  # (win=win,visible=False)
mouse.setExclusive(True)  # mouse input will be meaningless while this is set to True

# 0 did not work for the ticks. That is why we use responses between 1 and 2.
# slider = visual.Slider(win, ticks=sliderTicks, labelColor='Black', lineColor='Black', labels=list(sliderTicks),
#                        granularity=0, font=font_name, size=[textWrap, textHeight], pos=sliderPos, units='norm')
slider = visual.Slider(win, ticks=[1, 2, 3, 4], labelColor='Black', lineColor='Black', labels=['1 \n guess', 2, 3, '4 \n  certain'],
                               granularity=4, font=font_name, size=[textWrap, textHeight], units='norm')

# Setup TrialHandler
exp_handler = data.ExperimentHandler(dataFileName=data_file_name.format(**exp_info, dataType='crashSave'))

# Initialise messages
message = visual.TextStim(win, color='black', text='', font=font_name, height=textHeight, wrapWidth=textWrap)
messageResponseScreen = visual.TextStim(win, color='black',
                                        text='Was a scene change present? \n \n no                yes',
                                        font=font_name, height=textHeight, wrapWidth=textWrap)
messageCertain = visual.TextStim(win, color='black', text='How certain are you?',
                                 font=font_name, height=textHeight, wrapWidth=textWrap, pos=(0, 0.2))


#%% Instructions

# if playInstructions == True:
#
#     # Select instructions based on presentation order by removing instructions for question we present second.
#     instructionFiles = os.listdir(instruction_path)
#     instructionFiles.remove('instruction2_{}.png'.format(questionOrder[1]))  # Remove unused second instruction set
#
#     for instruction_image in instructionFiles:
#         if '.png' in instruction_image:  # Ignore other non-image files
#             instruction = visual.ImageStim(win, image=instruction_path + instruction_image)
#             instruction.draw()
#             win.flip()
#             event.waitKeys(keyList=continueKey)


#%% Experiment

trialListExp = pd.read_csv('trialList/trialList_changeDetection.csv')

# Select ramdom sample of trials for practise
trialListPractise = trialListExp.sample(n=num_practise).copy()

getrandpos(trialListPractise)
getrandpos(trialListExp)


# Instantiate variables to be faster in the loop

stimulus_dict = {}
for s in targ_distr_dict+['scene1', 'scene2', 'occluder']:
    stimulus_dict[s] = visual.ImageStim(win, pos=imagePos, size=imageSize)

stim_scene = Image.open(stim_path + 'scene.png')

img_name_occluder = ''
img_name_scene = ''

trialStartFlip = expClock.getTime()
occluderFlip = expClock.getTime()
scene1Flip = expClock.getTime()
scene2Flip = expClock.getTime()

ISI = core.StaticPeriod(win=win, screenHz=screenRefresh)

blockNum = 1

for block in expBlocks:

    trials_current_block = trialListPractise if 'practise' in block else trialListExp
    file_dict_list = trials_current_block.to_dict('records') # TrialHandler needs a list of dictionaries

    trials = data.TrialHandler(file_dict_list,
                               repetitionsPractise if 'practise' in block else repetitionsExp,
                               method='random')  # Random will block repetitions.

    exp_handler.addLoop(trials)
    # stimulus_path = stim_path+'/practise/' if 'practise' in block else stim_path

    if 'practise' in block:
        textMessage('Press space to start practise trials.')

    trialNum = 1
    for currentTrial in trials:
        print(currentTrial)

        # Inter stimulus interval
        win.flip()  # First flip: Send flip to display, but script does not wait until display is updated
        win.flip()  # Second flip: This flip must wait until the screen finishes updating the previous flip
        trialStartFlip = expClock.getTime()  # Gets the time when the screen was updated with the first flip

        ISI.start(ISI_duration-0.006)

        stimulus_dict['occluder'].image = stim_path+'occluder_{}.png'.format(currentTrial['occluder']) if 'scene' not in currentTrial['occluder'] else stim_path+'scene.png'

        for sce_num in ['scene1', 'scene2']:
            stim_scene = Image.open(stim_path + 'scene.png')
            for stim_elem in targ_distr_dict:

                # The positions stored under the position column are randomised.
                # We can therefore use the target/distractor number to put them in corresponding positions:
                # target1 in pos1, target2 in pos2, distractor3 in pos3, ...
                stim_scene.alpha_composite(Image.open(stim_path
                                                      + currentTrial[stim_elem]  # Gives a fruit
                                                      + '_'
                                                      + str(int(currentTrial['pos'+stim_elem[-1]
                                                                             +'_'+sce_num]))
                                                      + '.png'))
            stimulus_dict[sce_num].image = stim_scene

        stimulus_dict['scene1'].draw()

        ISI_success = ISI.complete()
        print(ISI_success)

        # Scene 1
        win.flip()
        stimulus_dict['scene1'].draw()
        win.flip()
        scene1Flip = expClock.getTime()

        stimulus_dict['occluder'].draw()

        while expClock.getTime() < scene1Flip + scene1Duration - 0.010:  # 0.0105 # 0.0089:
            pass

        # Occluder stimulus
        win.flip()
        stimulus_dict['occluder'].draw()
        win.flip()
        occluderFlip = expClock.getTime()

        stimulus_dict['scene2'].draw()

        # Deduct small amount of time to account for the time it takes to buffer the images in the code above
        while expClock.getTime() < occluderFlip + occluderDuration - 0.0127:  # 0.0082:
            pass

        # Scene 2
        win.flip()
        stimulus_dict['scene2'].draw()
        win.flip()
        scene2Flip = expClock.getTime()

        messageResponseScreen.draw()

        while expClock.getTime() < scene2Flip + scene2Duration - 0.010:  # 0.0105 # 0.0089:
            pass

        # Rating scene change
        win.flip()
        messageResponseScreen.draw()
        win.flip()
        resp_screen_flip = expClock.getTime()

        keyPress = event.waitKeys(keyList=responseKeys)

        # Rating certain
        slider.draw()
        messageCertain.draw()
        win.flip()
        ratingCertain = event.waitKeys(keyList=responseKeysRating)

        # Add responses to handler
        exp_handler.addData('trial_start', trialStartFlip-exp_tick_ref)
        exp_handler.addData('time_on_flip_scene1', scene1Flip - exp_tick_ref)
        exp_handler.addData('time_on_flip_occluder', occluderFlip - exp_tick_ref)
        exp_handler.addData('time_on_flip_scene2', scene2Flip-exp_tick_ref)
        exp_handler.addData('time_on_flip_response_screen', resp_screen_flip)

        exp_handler.addData('yesno_detection', keyPress)
        exp_handler.addData('rating_certain', ratingCertain)

        exp_handler.addData('block', blockNum)
        exp_handler.addData('trial', trialNum)
        # exp_handler.addData('pressed_multi', True if len(resp0)>1 or len(resp1)>1 else False)

        exp_handler.nextEntry()

        print('Finished, trial', trialNum, block, 'block')
        checkQuit()  # interrupt experiment if key combination matches

        # Take a break if trial can be divided by breakTrial and if it is not the last trial in a block
        if (trialNum % breakTrial == 0) and (trialNum != trials.nTotal):
            takeBreak()
        trialNum += 1

    if 'practise' in block:
        textMessage('Finished practise trials. \n Press space to start the experiment.')
    
    blockNum += 1


#%% Save data and close experiment

exp_handler.saveAsWideText(fileName=data_file_name.format(**exp_info, dataType='trialData'), delim=',')
pd.DataFrame(exp_info, index=[0]).to_csv(data_file_name.format(**exp_info, dataType='expInfo')+'.csv')

textMessage('Experiment finished. \n Thank you for your participation.', key_to_wait='escape')

quitExperiment()
