# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 13:17:07 2024
"""

# %% ToDo
# Change in instruction text: Wortlaut der Items
# event.waitKeys() does not wait until button is released


#%%

from psychopy import visual, core, data, gui, logging, event
import os
import pandas as pd
import sys


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


# %% Set variables

debug = False
# playInstructions = False

repetitionsExp = 1
repetitionsPractise = 1

# {} because we will use .format() for these fields later on
data_folder_path = "data/sub-{ID}"
data_file_name = data_folder_path+"/sub-{ID}_{dataType}"
instruction_path = "instructions/"

screenResolution = (1920, 1080)
imageSize = [0.95, 0.95]

ISI_duration = 1.0  # Time in seconds
occluderDuration = 4.0  # Time in seconds
sceneDuration = 1.0  # Time in seconds
breakTime = 60.0  # Time in seconds. Duration of the break.
breakTrial = 60  # Number of trials after which to make a break
waitBetweenItems = 0.2  # Seconds

textHeight = 0.08  # 50
textWrap = 0.8  # 1.5  # 1500

# sliderTicks = (range(5))

font_name = 'Arial'  # Slider has difficulties with some other fonts
continueKey = ['space']
responseKeys = [str(num) for num in list(range(1, 10))]


if debug == True:
    occluderDuration = 1.0
    breakTime = 1.0

#%%

# GUI (present before defining window, because fullscr prevents interaction with other windows)
# * makes gui fields mandatory
exp_info = {
    'Task*': ['-- select input --', 'sequential', 'side-by-side'],
    'First question*': ['-- select input --', 'imagine', 'likely'],
    'ID*': '',
    'Age*': '',
    'Gender*': ['-- select input --', 'female', 'male', 'diverse']
}

infoDlg = gui.DlgFromDict(exp_info, title='IASD '+data.getDateStr(), sortKeys=False)
if not infoDlg.OK:  # Stop experiment if participant pressed cancel
    print('Experiment cancelled')
    core.quit()
elif infoDlg.OK == True and '-- select input --' in [exp_info['Gender*'],  # Check if gender and block order is selected
                                                     exp_info['First question*'],
                                                     exp_info['Task*']]:
    raise ValueError('Experiment stopped. Please fill in all fields.')

# Remove * from dictionary keys
for key in list(exp_info.keys()):  # Use list to make a copy of the object
    exp_info[key[0:-1]] = exp_info.pop(key)  # Remove the old key (pop) and replace with new name (key[0:-1])

exp_info['date'] = data.getDateStr()  # Add a date field to dict

# set visibility fixation cross
alphaVal = 0

# Set presentation order of blocks
expBlocks = ['practise', 'experiment']

# Set experiment task
if exp_info['Task'] == 'sequential':
    imagePosOccl = [-0.5, 0]
    imagePosScene = [-0.5, 0]
    sliderPos = [0.5, 0]
elif exp_info['Task'] == 'side-by-side':
    imagePosOccl = [-0.5, 0.5]
    imagePosScene = [-0.5, -0.5]
    sliderPos = [0.5, 0]

# Set order of questions
if exp_info['First question'] == 'imagine':
    questionOrder = ['imagine', 'likely']
elif exp_info['First question'] == 'likely':
    questionOrder = ['likely', 'imagine']

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

# Setup TrialHandler
exp_handler = data.ExperimentHandler(dataFileName=data_file_name.format(**exp_info, dataType='crashSave'))

# Initialise messages
message = visual.TextStim(win, color='black', text='', font=font_name, height=textHeight, wrapWidth=textWrap)
# messageResponseScreen = visual.TextStim(win, color='black', text='', font=font_name, pos=(sliderPos[0], 0.4), height=textHeight, wrapWidth=textWrap)

# Create a fixation cross
fixation_cross = visual.TextStim(win, color=[-1, -1, -1], opacity=alphaVal, text='+', height=textHeight)


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

# Instantiate variables to be faster in the loop
stimulus_occluder = visual.ImageStim(win, pos=imagePosOccl, size=imageSize)
stimulus_scene = visual.ImageStim(win, pos=imagePosScene, size=imageSize)

scale0 = visual.ImageStim(win,
                          pos=sliderPos,
                          image='rating_scale/{}_1.png'.format(questionOrder[0]),
                          size=imageSize)
scale1 = visual.ImageStim(win,
                          pos=sliderPos,
                          image='rating_scale/{}_2.png'.format(questionOrder[1]),
                          size=imageSize)

img_name_occluder = ''
img_name_scene = ''

trialStartFlip = expClock.getTime()
occluderFlip = expClock.getTime()
sceneFlip = expClock.getTime()
rating0lip = expClock.getTime()
rating1Flip = expClock.getTime()
item0_rt = expClock.getTime()
item1_rt = expClock.getTime()

ISI = core.StaticPeriod(win=win, screenHz=screenRefresh)

blockNum = 1
for block in expBlocks:
    trials = data.TrialHandler('trialList/trialList_IASD_exp1_{}.csv'.format(block),
                               repetitionsPractise if 'practise' in block else repetitionsExp,
                               method='random')  # Random will block repetitions.
    exp_handler.addLoop(trials)
    stimulus_path = '../stimuli/stimuli/practise/' if 'practise' in block else '../stimuli/stimuli/'

    if 'practise' in block:
        textMessage('Press space to start practise trials.')

    trialNum = 1
    # win.flip()  # initial flip to be in sync with the monitor in the loop
    for currentTrial in trials:

        # Inter stimulus interval
        fixation_cross.draw()
        win.flip()  # First flip: Send flip to display, but script does not wait until display is updated
        fixation_cross.draw()
        win.flip()  # Second flip: This flip must wait until the screen finishes updating the previous flip
        trialStartFlip = expClock.getTime()  # Gets the time when the screen was updated with the first flip

        ISI.start(ISI_duration-0.006)
        stimulus_occluder.image = stimulus_path + currentTrial['occluderFile']
        stimulus_scene.image = stimulus_path + currentTrial['fruitFile']
        stimulus_occluder.draw()
        fixation_cross.draw()  # Second draw on top
        ISI.complete()

        # Occluder stimulus
        win.flip()
        stimulus_occluder.draw()
        fixation_cross.draw()
        win.flip()
        occluderFlip = expClock.getTime()

        stimulus_occluder.draw()  # not visible in sequential condition
        stimulus_scene.draw()
        fixation_cross.draw()

        # Deduct small amount of time to account for the time it takes to buffer the images in the code above
        while expClock.getTime() < occluderFlip + occluderDuration - 0.0127:  # 0.0082:
            pass

        # Scene stimulus
        win.flip()
        stimulus_occluder.draw()
        stimulus_scene.draw()
        fixation_cross.draw()
        win.flip()
        sceneFlip = expClock.getTime()

        stimulus_occluder.draw()
        stimulus_scene.draw()
        scale0.draw()

        while expClock.getTime() < sceneFlip + sceneDuration - 0.010:  # 0.0105 # 0.0089:
            pass

        # Rating scale 0
        win.flip()
        stimulus_occluder.draw()
        stimulus_scene.draw()
        scale0.draw()
        win.flip()
        rating0Flip = expClock.getTime()

        resp0 = event.waitKeys(keyList=responseKeys)
        rating0_rt = expClock.getTime()

        core.wait(waitBetweenItems)

        # Rating scale 1
        stimulus_occluder.draw()
        stimulus_scene.draw()
        scale1.draw()
        win.flip()

        stimulus_occluder.draw()
        stimulus_scene.draw()
        scale1.draw()
        win.flip()
        rating1Flip = expClock.getTime()

        resp1 = event.waitKeys(keyList=responseKeys)
        rating1_rt = expClock.getTime()

        # print((occluderFlip - trialStartFlip) * 1000, (sceneFlip - occluderFlip) * 1000,
        #       (rating0Flip - sceneFlip) * 1000, questionOrder[0])


        # Add responses to handler
        exp_handler.addData('{}_rating'.format(questionOrder[0]), resp0)
        exp_handler.addData('{}_rating'.format(questionOrder[1]), resp1)
        exp_handler.addData('{}_time_on_response'.format(questionOrder[0]), rating0_rt-exp_tick_ref)
        exp_handler.addData('{}_time_on_response'.format(questionOrder[1]), rating1_rt-exp_tick_ref)

        exp_handler.addData('trial_start', trialStartFlip-exp_tick_ref)
        exp_handler.addData('time_on_flip_occluder', occluderFlip-exp_tick_ref)
        exp_handler.addData('time_on_flip_scene', sceneFlip-exp_tick_ref)
        exp_handler.addData('{}_scale_time_on_flip'.format(questionOrder[0]), rating0Flip - exp_tick_ref)
        exp_handler.addData('{}_scale_time_on_flip'.format(questionOrder[1]), rating1Flip - exp_tick_ref)

        exp_handler.addData('block', blockNum)
        exp_handler.addData('trial', trialNum)
        exp_handler.addData('pressed_multi', True if len(resp0)>1 or len(resp1)>1 else False)

        exp_handler.nextEntry()

        print('Finished, trial', trialNum, 'block', block)
        checkQuit()  # interrupt experiment if key combination matches

        # Take a break if trial can be divided by breakTrial and if it is not the last trial in a block
        if (trialNum % breakTrial == 0) and (trialNum != trials.nTotal):
            takeBreak()
        trialNum += 1

        # fixation_cross.draw()
        # win.flip()  # Flip to get script in sync with monitor on next trial

    if 'practise' in block:
        textMessage('Finished practise trials. \n Press space to start the experiment.')
    
    blockNum += 1


#%% Save data and close experiment

exp_handler.saveAsWideText(fileName=data_file_name.format(**exp_info, dataType='trialData'), delim=',')
pd.DataFrame(exp_info, index=[0]).to_csv(data_file_name.format(**exp_info, dataType='expInfo')+'.csv')

textMessage('Experiment finished. \n Thank you for your participation.', key_to_wait='escape')

quitExperiment()
