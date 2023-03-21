#!/usr/bin/python

"""
sense.py
"""

import sys

from numpy import sqrt
from scientisst import *
from scientisst import __version__
from threading import Timer
from threading import Event
from sense_src.arg_parser import ArgParser
from sense_src.custom_script import get_custom_script, CustomScript
from sense_src.device_picker import DevicePicker
from sense_src.file_writer import *


def run_scheduled_task(duration, stop_event):
    def stop(stop_event):
        stop_event.set()

    timer = Timer(duration, stop, [stop_event])
    timer.start()
    return timer


def main():
    arg_parser = ArgParser()
    args = arg_parser.args

    if args.version:
        sys.stdout.write("sense.py version {}\n".format(__version__))
        sys.exit(0)

    if args.address:
        address = args.address
    else:
        if args.mode == COM_MODE_BT:
            address = DevicePicker().select_device()
            if not address:
                arg_parser.error("No paired device found")
        else:
            arg_parser.error("No address provided")

    args.channels = sorted(map(int, args.channels.split(",")))

    scientisst = ScientISST(address, com_mode=args.mode, log=args.log)

    try:
        if args.output:
            firmware_version = scientisst.version_and_adc_chars(print=False)
            file_writer = FileWriter(
                args.output,
                address,
                args.fs,
                args.channels,
                args.convert,
                __version__,
                firmware_version,
            )
        if args.stream:
            from sense_src.stream_lsl import StreamLSL

            lsl = StreamLSL(
                args.channels,
                args.fs,
                address,
            )
        if args.script:
            script = get_custom_script(args.script)

        stop_event = Event()

        scientisst.start(args.fs, args.channels)
        sys.stdout.write("Start acquisition\n")

        if args.output:
            file_writer.start()
        if args.stream:
            lsl.start()
        if args.script:
            script.start()

        timer = None
        if args.duration > 0:
            timer = run_scheduled_task(args.duration, stop_event)
        try:
            if args.verbose:
                header = "\t".join(get_header(args.channels, args.convert)) + "\n"
                #sys.stdout.write(header)
            res = np.zeros(50)
            maxi_z = 994.58
            mini_z = 562.52
            mini_y = 544.42
            maxi_y = 976.14
            mini_x = 539.4
            maxi_x = 979.52
            maxi = 0
            mini = 10000
            itere = 0
            while not stop_event.is_set():
                frames = scientisst.read(convert=args.convert, matrix=True)
                if args.output:
                    file_writer.put(frames)
                if args.stream:
                    lsl.put(frames)
                if args.script:
                    script.put(frames)
                #if args.verbose:
                    #sys.stdout.write("{}\n".format(frames[0]))
                
                for element in frames:
                    
                    itere = itere +1
                   
                    #print([element[0]]+[element[-7]]+[element[-5]]+[element[-3]]+[element[-1]])
                    
                    #res = np.append(res[1:],[element[-5]])
                    #print(element)
                    acc_x = (element[-4] - mini_x)/(maxi_x-mini_x)*2-1
                    acc_y = (element[-2] - mini_y)/(maxi_y-mini_y)*2-1
                    acc_z = (element[-6] - mini_z)/(maxi_z-mini_z)*2-1
                    acc = sqrt(acc_x**2+acc_y**2+ acc_z**2)
                    print(acc)
                    
                    
                    '''
                    res = np.append(res[1:],[element[-6]])
                    if itere > 50:
                        ave_mary = np.average(res)
                        if ave_mary > maxi:
                            maxi = ave_mary
                            
                        if ave_mary < mini:
                            mini = ave_mary
                        #print(maxi , mini)
                    #print(element[-1])
                    #print([element[-7]]+[aceler])'''
        except KeyboardInterrupt:
            if args.duration and timer:
                timer.cancel()
            pass

        scientisst.stop()
        # let the acquisition stop before stoping other threads
        time.sleep(0.25)

        sys.stdout.write("Stop acquisition\n")
        if args.output:
            file_writer.stop()
        if args.stream:
            lsl.stop()
        if args.script:
            script.stop()

    finally:
        scientisst.disconnect()

    sys.exit(0)


if __name__ == "__main__":
    main()
