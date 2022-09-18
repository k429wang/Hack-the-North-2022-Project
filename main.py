# Hack the North 2022 Project Submission
# By Kai Wang, Keegan Liu, Joey Wang, and Freeman Huang
# Attribution: https://github.com/adhawkmicrosystems/python-sdk-examples

import adhawkapi
import adhawkapi.frontend
from adhawkapi import MarkerSequenceMode, PacketType, Events
from playsound import playsound

import time, sys, os, threading

# SETUP STUFF FOR GCLOUD
from google.cloud import vision, translate, texttospeech
from google.cloud import translate
import io, os, re, sys

import cv2
import numpy as np

from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("hackthenorth-1663435360245-76d2e298297d.json")

native_language = "en-US"

# file path
output_path = 'output'

# note: portugues(portugal), english(british) have the same language codes and do not need to be converted
language_map = {"zh-CN":"zh-Hans", "zh-TW":"zh-Hant", "pt-BR":"pt"}

# IMPORT FUNCTIONS FROM text-recognition
from textrecognition import *

class Frontend:
    ''' Frontend communicating with the backend '''

    def __init__(self):
        # Instantiate an API object
        self._api = adhawkapi.frontend.FrontendApi()

        # Tell the api that we wish to tap into the GAZE IN IMAGE data stream
        # with self._handle_gaze_data_stream as the handler
        self._api.register_stream_handler(PacketType.GAZE_IN_IMAGE, self._handle_gaze_in_image_stream)

        # Tell the api that we wish to tap into the EVENTS stream
        # with self._handle_event_stream as the handler
        self._api.register_stream_handler(PacketType.EVENTS, self._handle_event_stream)

        # Instantiate and start a video receiver with self._handle_video_stream as the handler for new frames
        self._video_receiver = adhawkapi.frontend.VideoReceiver()
        self._video_receiver.frame_received_event.add_callback(self._handle_video_stream)
        self._video_receiver.start()

        self._video_receiver_address = self._video_receiver.address

        # Start the api and set its connection callback to self._handle_connect_response. When the api detects a
        # connection to a MindLink, this function will be run.
        self._api.start(connect_cb=self._handle_connect_response)

        # Disallows console output until a Quick Start has been run
        self._allow_output0 = False
        self._allow_output1 = False

        # Used to limit the rate at which data is displayed in the console
        self._last_console_print = None

        # Initialize the gaze coordinates to dummy values for now
        self._gaze_coordinates = []

        # Initialize blink duration, last blink timer, and crop boundaries to dummy values for now
        self._blink_duration = 0
        self.last_blink = 0
        self.crop_boundaries = []

        # Initialize a counter for image file names
        self.img_counter = 0
        self.len_changed = False

        self.timestamp = 0

        # Flags the frontend as not connected yet
        self.connected = False
        print('Starting frontend...')

    def _handle_camera_start_response(self, error):

        # Handles the response after starting the tracker's camera
        if error:
            # End the program if there is a camera error
            print(f'Camera start error: {error}')
            self.shutdown()
            sys.exit()
        else:
            # Otherwise, starts the video stream, streaming to the address of the video receiver
            self._api.start_video_stream(*self._video_receiver_address, lambda *_args: None)

    def shutdown(self):
        ''' Shuts down the backend connection '''
        # Stops the video stream
        self._api.stop_video_stream(*self._video_receiver_address, lambda *_args: None)

        # Stops api camera capture
        self._api.stop_camera_capture(lambda *_args: None)

        # Stop the log session
        self._api.stop_log_session(lambda *_args: None)

        # Shuts down the api
        self._api.shutdown()

    def _handle_gaze_in_image_stream(self, timestamp, gaze_img_x, gaze_img_y, *_args):

        # Updates the gaze marker coordinates with new gaze data. It is possible to receive NaN from the api, so we
        # filter the input accordingly.
        self._gaze_coordinates = [gaze_img_x, gaze_img_y]
        self.timestamp = timestamp

        # Only log at most once per second
        # if self._last_console_print and timestamp < self._last_console_print + 1:
        #     return

        # if self._allow_output0 and self._allow_output1:
        #     self._last_console_print = timestamp
        #     print(f'Gaze data\n'
        #           f'Time since connection:\t{timestamp}\n'
        #           f'X coordinate:\t\t{gaze_img_x}\n'
        #           f'Y coordinate:\t\t{gaze_img_y}\n')

    def _handle_event_stream(self, event_type, timestamp, *args):
        ''' Prints event data to the console '''
        if self._allow_output0 and self._allow_output1:
            # We discriminate between events based on their type
            if event_type == Events.BLINK.value: # BLINK EVENT
                print('Blink!')
                # Only detect double blink if the second blink happens less than 1 second after previous blink
                if self.last_blink > 0 and timestamp < self.last_blink + 0.75:
                    self.last_blink = 0 
                    t = threading.Timer(1, self.double_blink_handler)
                    t.start()
                else:
                    self.last_blink = timestamp
                self._blink_duration = args[0]

    def double_blink_handler(self):
        print("DOUBLE BLINK")
        self.crop_boundaries.append(self._gaze_coordinates)
        print(self._gaze_coordinates)
        self.len_changed = True
        if ((len(self.crop_boundaries) == 2) and (self.len_changed == True)):
            print("2")
            self.crop()
            self.crop_boundaries = []
            self.len_changed = False     
            #os.remove("images\img.jpeg")
            #TO RETURN

    def _handle_connect_response(self, error):
        ''' Handler for backend connections '''

        # Starts the camera and sets the stream rate
        if not error:
            print('Connected to AdHawk Backend Service')

            # Sets the GAZE data stream rate to 125Hz
            self._api.set_stream_control(PacketType.GAZE_IN_IMAGE, 125, callback=(lambda *_args: None))

            # self._api.set_camera_user_settings(adhawkapi.CameraUserSettings.PARALLAX_CORRECTION, 1)

            # Tells the api which event streams we want to tap into. In this case, we wish to tap into the BLINK and
            # SACCADE data streams.
            self._api.set_event_control(adhawkapi.EventControlBit.BLINK, 1, callback=(lambda *_args: None))
            self._api.set_event_control(adhawkapi.EventControlBit.SACCADE, 1, callback=(lambda *_args: None))

            # Starts the MindLink's camera so that a Quick Start can be performed. Note that we use a camera index of 0
            # here, but your camera index may be different, depending on your setup. On windows, it should be 0.
            # self._api.start_camera_capture(camera_index=0, resolution_index=adhawkapi.CameraResolution.MEDIUM,
            #                                correct_distortion=False, callback=(lambda *_args: None))

            # Starts the tracker's camera so that video can be captured and sets self._handle_camera_start_response as
            # the callback. This function will be called once the api has finished starting the camera.
            self._api.start_camera_capture(camera_index=0, resolution_index=adhawkapi.CameraResolution.MEDIUM,
                                           correct_distortion=False, callback=self._handle_camera_start_response)

            # Starts a logging session which saves eye tracking signals. This can be very useful for troubleshooting
            self._api.start_log_session(log_mode=adhawkapi.LogMode.BASIC, callback=lambda *args: None)

            # Flags the frontend as connected
            self.connected = True

    def _handle_video_stream(self, _gaze_timestamp, _frame_index, image_buf, _frame_timestamp):
        if (len(self.crop_boundaries) == 1) and (self.len_changed == True):
            print("1")
            with open("images\img"+str(self.img_counter)+".jpeg", 'wb') as fh:
                fh.write(image_buf)
            self.len_changed = False

    def calibrate(self):
        ''' Runs a Calibration using AdHawk Backend's GUI '''

        # Two
        #  calibration modes are supported: FIXED_HEAD and FIXED_GAZE
        # With fixed head mode you look at calibration markers without moving your head
        # With fixed gaze mode you keep looking at a central point and move your head as instructed during calibration.
        self._api.start_calibration_gui(mode=MarkerSequenceMode.FIXED_HEAD, n_points=9, marker_size_mm=35, randomize=False, callback=(lambda *_args: None))
        print("calibrate!")

    def quickstart(self):
        ''' Runs a Quick Start using AdHawk Backend's GUI '''

        # The MindLink's camera will need to be running to detect the marker that the Quick Start procedure will
        # display. This is why we need to call self._api.start_camera_capture() once the MindLink has connected.
        self._api.quick_start_gui(mode=MarkerSequenceMode.FIXED_GAZE, marker_size_mm=35, callback=(lambda *_args: None))
        print("quickstart!")

    def allow_output(self):
        self._allow_output1 = True
        self._allow_output0 = True

    def crop(self):
        print("CROPPED")
        # make sure to add some leeway to each coordinate boundary, in case the coordinates are off or something
        file_name = f"images/img{self.img_counter}.jpeg"
        self.img_counter += 1
        # GOOGLE CLOUD STUFF
        try:
            crop_image(file_name, int(self.crop_boundaries[0][0])-200, int(self.crop_boundaries[0][1])-150, int(self.crop_boundaries[1][0])+200, int(self.crop_boundaries[1][1])+150)
            read_image = detect_text("output/croppedimage.jpg")
            # read_image = detect_text("images/img.jpeg")
            read_language = detect_language(read_image)

            # check if language is consistent and needs to be remapped
            if read_language in language_map.keys():
                read_language = language_map[read_language]

            translated = translate_text(read_image, read_language, native_language)

            print(f"Read text: \n{read_image}")
            print(f"Language: {read_language}")
            print(f"Translated text:\n{translated}")
            tts(translated, output_path)
            playsound('output/output.mp3')

        except:
            playsound('output/bad.mp3')

def main():
    '''Main function'''

    frontend = Frontend()
    try:
        print('Plug in your MindLink and ensure AdHawk Backend is running.')
        while not frontend.connected:
            pass  # Waits for the frontend to be connected before proceeding

        input('Press Enter to run a Quick Start.')

        # Runs a Quick Start at the user's command. This tunes the scan range and frequency to best suit the user's eye
        # and face shape, resulting in better tracking data. For the best quality results in your application, you
        # should also perform a calibration before using gaze data.
        frontend.quickstart()

        input('Press Enter to run a Calibration.')

        # Runs a Quick Start at the user's command. This tunes the scan range and frequency to best suit the user's eye
        # and face shape, resulting in better tracking data. For the best quality results in your application, you
        # should also perform a calibration before using gaze data.
        frontend.calibrate()

        input('Press Enter to start')

        frontend.allow_output()

        while True:
            # Loops while the data streams come in
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):

        # Allows the frontend to be shut down robustly on a keyboard interrupt
        frontend.shutdown()

if __name__ == '__main__':
    main()