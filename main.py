from crop_event import crop_event
from play_translation_audio import play_translation_audio
from screenshot_event import screenshot_event
from translation_event import translation_event

import adhawkapi
import adhawkapi.frontend
from adhawkapi import MarkerSequenceMode, PacketType, Events

import time, sys

class Frontend:
    ''' Frontend communicating with the backend '''

    def __init__(self):
        # Instantiate an API object
        self._api = adhawkapi.frontend.FrontendApi()

        # Tell the api that we wish to tap into the GAZE data stream
        # with self._handle_gaze_data_stream as the handler
        # self._api.register_stream_handler(PacketType.GAZE, self._handle_gaze_data_stream)

        # Tell the api that we wish to tap into the GAZE IN IMAGE data stream
        # with self._handle_gaze_data_stream as the handler
        self._api.register_stream_handler(PacketType.GAZE, self._handle_gaze_in_image_stream)

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
        self._gaze_coordinates = (0, 0, 0)

        # Initialize blink duration to dummy values for now
        self._blink_duration = 0
        self.last_blink = 0

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

    def _handle_gaze_data_stream(self, timestamp, x_pos, y_pos, z_pos, vergence):
        ''' Prints gaze data to the console '''

        # Only log at most once per second
        if self._last_console_print and timestamp < self._last_console_print + 1:
            return

        if self._allow_output0 and self._allow_output1:
            self._last_console_print = timestamp
            print(f'Gaze data\n'
                  f'Time since connection:\t{timestamp}\n'
                  f'X coordinate:\t\t{x_pos}\n'
                  f'Y coordinate:\t\t{y_pos}\n'
                  f'Z coordinate:\t\t{z_pos}\n'
                  f'Vergence angle:\t\t{vergence}\n')

    def _handle_gaze_in_image_stream(self, timestamp, gaze_img_x, gaze_img_y, *_args):

        # Updates the gaze marker coordinates with new gaze data. It is possible to receive NaN from the api, so we
        # filter the input accordingly.
        self._gaze_coordinates = [timestamp, gaze_img_x, gaze_img_y]

        # Only log at most once per second
        if self._last_console_print and timestamp < self._last_console_print + 1:
            return

        if self._allow_output0 and self._allow_output1:
            self._last_console_print = timestamp
            print(f'Gaze data\n'
                  f'Time since connection:\t{timestamp}\n'
                  f'X coordinate:\t\t{gaze_img_x}\n'
                  f'Y coordinate:\t\t{gaze_img_y}\n')

    def _handle_event_stream(self, event_type, timestamp, *args):
        ''' Prints event data to the console '''
        if self._allow_output0 and self._allow_output1:
            # We discriminate between events based on their type
            if event_type == Events.BLINK.value: # BLINK EVENT
                print('Blink!')
                # Only detect double blink if the second blink happens less than 1 second after previous blink
                if self.last_blink and timestamp < self.last_blink + 1:
                    self.double_blink_handler()
                self.last_blink = timestamp
                self._blink_duration = args[0]
            elif event_type == Events.SACCADE.value:
                print('Saccade!')

    def double_blink_handler(self):
        print("DOUBLE BLINK")
        self.last_blink = None 


    def _handle_connect_response(self, error):
        ''' Handler for backend connections '''

        # Starts the camera and sets the stream rate
        if not error:
            print('Connected to AdHawk Backend Service')

            # Sets the GAZE data stream rate to 125Hz
            self._api.set_stream_control(PacketType.GAZE, 125, callback=(lambda *_args: None))

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
        if self._blink_duration > 0.5:
            with open("images\img.jpeg", "wb") as fh:
                fh.write(image_buf)

    def calibrate(self):
        ''' Runs a Calibration using AdHawk Backend's GUI '''

        # Two calibration modes are supported: FIXED_HEAD and FIXED_GAZE
        # With fixed head mode you look at calibration markers without moving your head
        # With fixed gaze mode you keep looking at a central point and move your head as instructed during calibration.
        self._api.start_calibration_gui(mode=MarkerSequenceMode.FIXED_HEAD, n_points=9, marker_size_mm=35, randomize=False, callback=(lambda *_args: None))

        self._allow_output0 = True
        print("calibrate!")


    def quickstart(self):
        ''' Runs a Quick Start using AdHawk Backend's GUI '''

        # The MindLink's camera will need to be running to detect the marker that the Quick Start procedure will
        # display. This is why we need to call self._api.start_camera_capture() once the MindLink has connected.
        self._api.quick_start_gui(mode=MarkerSequenceMode.FIXED_GAZE, marker_size_mm=35, callback=(lambda *_args: None))
        
        self._allow_output1 = True
        print("quickstart!")


    def crop():
        print()

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

        while True:
            # Loops while the data streams come in
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):

        # Allows the frontend to be shut down robustly on a keyboard interrupt
        frontend.shutdown()

if __name__ == '__main__':
    main()