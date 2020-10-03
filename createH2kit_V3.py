#!/usr/bin/env python

import sys
import getopt
import string
import os.path
import tarfile

# ===============================================================================
#  this script (createH2kit.py) is a script that can help you with creating
#  drumkits for Hydrogen Advanced Drum Machine (www.hydrogen-music.org)
#  it is released under a CC BY-NC-SA license by Thijs Van Severen
#
#    V1    03/04/2012    : first version.  Created by Thijs Van Severen
#    V2    20/04/2012    : added espeak sample creator option (+fix some bugs)
#    V3    08/08/2020    : migrated to python 3 by Arve Barsnes
#
# ===============================================================================

# init

DrumSetName = "default name"
DrumSetAuthor = "default author"
DrumSetInfo = "default info"
DrumSetLicense = "default license"
DrumSetPath = ""
SampleArray = ""


def Help():

    print()
    print("createH2kit.py usage:")
    print("")
    print("This script helps you to create a Hydrogen drumkit.")
    print("There are 2 possible ways you can use this script : by providing your own")
    print("samples, or by providing a txt file that can be used to create espeak samples.")
    print("\n")
    print("1) Provide your own samples:")
    print("   This will create a drumkit from sample files you provide")
    print("")
    print(" - Manually create your samples (WAV, FLAC, AIFF) **")
    print(" - Place your samples in a temp dir")
    print(" - cd into the dir that holds this script and run the script like this :")
    print('     ./createH2kit_V2.py -i "/path/to/my/temp/dir/"')
    print(" - the script will ask you to enter some data about the kit you are creating")
    print(" - the drumkit will be created in the same dir where your samples are located")
    print(" - you can now import the H2drumkit file into Hydrogen via Instrument > Import library > Local File")
    print("")
    print(" ** IMPORTANT NOTE:")
    print(" The names of the wav/flac files _must_ follow the below naming scheme:")
    print("")
    print("   x-y instrument name.wav")
    print("")
    print("   x : the instrument ID (=position of this instrument in the drumkit)")
    print("   y : the layer ID (0=lowest velocity sample)")
    print("   instrument name : this is the name that will be used for the instrument")
    print("")
    print(" The rest of the script is interactive.")
    print("\n")
    print("2) Auto create espeak kit ")
    print("   This mode will create a 'voice-drumkit' using the espeak voice syntheses utility")
    print("")
    print(" - Create a text file that contains the words you want to use as samples ***")
    print(" - Place that file in a temp dir")
    print(" - cd into the dir that holds this script and run the script like this :")
    print('     ./createH2kit_V2.py -i "/path/to/my/temp/dir/my_text_file"')
    print(" - the script will ask you to enter some data about the kit you are creating")
    print(" - the drumkit will be created in the same dir where your text file is located")
    print(" - you can now import the H2drumkit file into Hydrogen via Instrument > Import library > Local File")
    print()
    print("")
    print(" *** IMPORTANT NOTE:")
    print(" The lines in your text file must be formatted as follows:")
    print("")
    print('   name of instrument * "text for espeak"')
    print("")
    print('   eg: Voice 1*"hello you"')
    print("   will create an instrument named 'Voice 1' that holds the 'hello you' espeak sample")
    print("")
    print(" You can also add the espeak options to the line:")
    print("")
    print('   eg: Voice 2*"hello you, how are you doing?" -s 50 -p 30')
    print("   will create an instrument named 'Voice 2' with an espeak sample at speed=50 and pitch=30")
    print(" For more options check the espeak man pages")
    print("\n\n")
    print("Available options are :")
    print(" -h, --help    : will display this help.")
    print(" -i, --input   : specifies the dir or file you want to use as input")
    print("                 if you specify a dir, the script will assume that")
    print("                 this dir contains your self-made samples.")
    print("                 if you specify a file, the script will assume that this")
    print("                 file contains the text you want to feed to espeak.")
    print(" -v, --verbose : generates extra debug output.")
    print(" -l, --listen  : will let espeak say the text from the input file you")
    print("                 specified, without generating any output files.")
    print("                 you can use this option to preview the espeak samples.")
    print("                 (does not work if you dont provide a file as input)")

    sys.exit(0)


def ConvertName(SampleFile):

    # strip off .wav or .flac
    FullName = (SampleFile.split('.'))[0]
    FileExt = (SampleFile.split('.'))[1]

    # split name on the spaces
    SplitName = FullName.split(' ')

    # first part is the 'full reference' that contains
    # the instrument nr + layer nr
    FullRef = SplitName[0]

    # part before the '-' is the instrument nr
    # part after the '-' is the layer nr
    InstrNr = int(FullRef.split('-')[0])
    InstrLayer = int(FullRef.split('-')[1])

    # instrument name is Fullname minus the fullref
    InstrName = string.strip(FullName.replace(FullRef, ''))

    if not InstrNr:
        print("no instr nr supplied")
    if not InstrLayer:
        print("no instr layer supplied")

    return (SampleFile, InstrNr, InstrLayer, InstrName, FileExt)


def AddInstrument(id, name):

    f.write('            <instrument>\n')
    f.write('                <id>' + str(id) + '</id>\n')
    f.write('                <name>' + name + '</name>\n')
    f.write('                <isMuted>false</isMuted>\n')
    f.write('                <isLocked>false</isLocked>\n')
    f.write('                <pan_L>1</pan_L>\n')
    f.write('                <pan_R>1</pan_R>\n')
    f.write('                <randomPitchFactor>0</randomPitchFactor>\n')
    f.write('                <gain>1</gain>\n')
    f.write('                <filterActive>false</filterActive>\n')
    f.write('                <filterCutoff>1</filterCutoff>\n')
    f.write('                <filterResonance>0</filterResonance>\n')
    f.write('                <Attack>0</Attack>\n')
    f.write('                <Decay>0</Decay>\n')
    f.write('                <Sustain>1</Sustain>\n')
    f.write('                <Release>1000</Release>\n')
    f.write('                <muteGroup>-1</muteGroup>\n')


def AddLayer(SampleFile, NumOfLayers, LayerNr):

    print(("    add layer " + str(LayerNr) + " (" + SampleFile + ")"))

    # calculate min/max velocity range according to what layer we are adding
    # for this instrument + how many layers there are for this instrument
    MinVelocity = round((1.0/NumOfLayers)*(LayerNr-1), 2)
    MaxVelocity = round((1.0/NumOfLayers)*LayerNr, 2)
    velocitystring = str(MinVelocity) + " - " + str(MaxVelocity)

    print(("       velocity range : " + velocitystring))

    f.write('                <layer>\n')
    f.write('                    <filename>' + SampleFile + '</filename>\n')
    f.write('                    <min>' + str(MinVelocity) + '</min>\n')
    f.write('                    <max>' + str(MaxVelocity) + '</max>\n')
    f.write('                    <gain>1</gain>\n')
    f.write('                    <pitch>0</pitch>\n')
    f.write('                </layer>\n')


def main():

    global DrumSetName
    global DrumSetAuthor
    global DrumSetInfo
    global DrumSetLicense
    global DrumSetPath
    global Verbose, Listen
    # global SampleArray
    # SampleArray = []
    Verbose = False
    Listen = False
    Input = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hi:vl",
                                   ["help", "input=", "verbose", "listen"])
    except getopt.GetoptError as err:
        # print help information and exit:
        # will print something like "option -a not recognized"
        return "Error: %s" % str(err)
    except Exception:
        return "Something went wrong !"

    if not opts:
        returnvalue1 = "Arguments expected for this script\n"
        returnvalue2 = "Run script with -h or --help option for more info"
        return returnvalue1 + returnvalue2
    else:
        for o, a in opts:
            if o in ("-h", "--help"):
                Help()
            elif o in ("-i", "--input"):
                Input = a
            elif o in ("-v", "--verbose"):
                Verbose = True
            elif o in ("-l", "--listen"):
                Listen = True

    if not Input:
        returnvalue1 = "No input file or path specified\n"
        returnvalue2 = "Use the '-i' or '--input' option to specify this, "
        returnvalue3 = " or run the script with '-h' for more info"
        return returnvalue1 + returnvalue2 + returnvalue3

    if Verbose:
        print(("input = " + str(Input)))

    if os.path.isfile(Input):
        print("input is a file > assuming this is a espeak h2 file")
        return CreateEspeakFiles(Input)

    # check path
    if os.path.exists(Input):
        print("input is path > assuming this dir contains audio files")
        return CreateDrumkit(Input)
    else:
        return "The path you entered (" + Input + ") does not exist"


def CreateEspeakFiles(InputFile):

    print("create espeak files")
    FilePath = os.path.dirname(InputFile)
    print(("filepath = " + str(FilePath)))
    f = open(InputFile, "r")
    bla = f.readlines()

    Instrument = 1
    for line in bla:
        if "*" not in line:
            print(("skipping line " + str(line)))
            print("line format not OK (missing '*')")
        else:

            # split up the line in 'instrument name' and 'text for espeak'
            foo = line.rstrip('\n')
            foo = str(foo).split('*')
            print(("instrument = " + str(foo[1])))

            # create filename :
            # path + instrument couter + '-1' + the filename + 'wav'
            # this should give something like 'path/1-1 name.wav'
            pathandid = FilePath + "/" + str(Instrument) + "-1 "
            filename = pathandid + str(foo[0]) + ".wav"
            print(("filename = " + str(filename)))

            if Listen:
                command = 'espeak ' + foo[1]
            else:
                command = 'espeak ' + foo[1] + ' -w "' + filename + '"'

            print(("command " + str(command)))
            os.system(command)
            # os.system("ls")
            Instrument += 1

    if Listen:
        return "OK"
    else:
        return CreateDrumkit(FilePath + "/")


def CreateDrumkit(DrumSetPath):
    # enter drumkit data

    global f
    SampleArray = []
    InstrumentLayers = []
    MaxInstrumentID = 0
    InstrumentLayersDct = {}

    print()
    print("Please enter the drumkit info:")
    DrumSetName = eval(input('Please enter the drumkit name: '))
    DrumSetAuthor = eval(input('Please enter the name of the author: '))
    DrumSetInfo = eval(input('Please enter any extra info you want to add: '))
    DrumSetLicense = eval(input('Please enter the drumkit license type: '))
    print()

    if not DrumSetName:
        if Verbose:
            print("No name entered for the drumkit. Using 'drumkit")
        DrumSetName = "drumkit"

    # check what files are available in the dir
    WavFiles = 0
    FlacFiles = 0

    for SampleFile in os.listdir(DrumSetPath):
        print(("filename : " + SampleFile))
        if ".WAV" in SampleFile.upper():
            WavFiles += 1
        elif ".FLAC" in SampleFile.upper():
            FlacFiles += 1

        # print(("convertname : " + str(ConvertName(SampleFile))))

        if (".FLAC" in SampleFile.upper()) or (".WAV" in SampleFile.upper()):
            SampleArray.append(ConvertName(SampleFile))

    if (WavFiles + FlacFiles == 0):
        aborttext = "ABORTING: no sample files (.wav or .flac) found in "
        return aborttext + DrumSetPath

    # count the number of layers each instrument has
    # we need this info later to determine the min and max layer velocity
    for i in range(len(SampleArray)):
        LayerCount = 0
        for j in range(len(SampleArray)):
            if SampleArray[j][1] == SampleArray[i][1]:
                LayerCount += 1

        # print(("instrument nr : " +
        #        str(SampleArray[i][1]) +
        #        " has " +
        #        str(LayerCount) +
        #        " layers"))
        foo = (SampleArray[i][1], LayerCount)
        # do not store duplicate values
        if foo not in InstrumentLayers:
            InstrumentLayers.append(foo)

    sorted(set(InstrumentLayers))
    # print(("instr layers : " + str(InstrumentLayers)))

    # create dictionary from instrument layer list
    for i in range(0, len(InstrumentLayers), 1):
        InstrumentLayersDct[InstrumentLayers[i][0]] = InstrumentLayers[i][1]

    # find out what the highest instrument ID is
    # and how many instruments we have
    MaxInstrumentID = (max(InstrumentLayers))[0]
    NumberOfInstruments = len(InstrumentLayers)

    print("Kit info :")
    print(("Drumset name      : " + DrumSetName))
    print(("Author name       : " + DrumSetAuthor))
    print(("Info              : " + DrumSetInfo))
    print(("License           : " + DrumSetLicense))
    print(("Drumkit Path      : " + DrumSetPath))
    print(("Instruments found : " + str(NumberOfInstruments)))
    print((".wav files found  : " + str(WavFiles)))
    print((".flac files found : " + str(FlacFiles)))

    filename = DrumSetPath + "drumkit.xml"

    try:
        f = open(filename, "w")
        f.write('<drumkit_info>\n')
        f.write('    <name>' + DrumSetName + '</name>\n')
        f.write('    <author>' + DrumSetAuthor + '</author>\n')
        f.write('    <info>' + DrumSetInfo + '</info>\n')
        f.write('    <license>' + DrumSetLicense + '</license>\n')
        f.write('    <instrumentList>\n')

        # first sort according to layer nr ...
        SampleArray.sort(key=lambda a: a[2])

        # ... and then sort by instrument nr
        SampleArray.sort(key=lambda a: a[1])

        # add instruments and layers to xml file
        for InstrumentPos in range(1, int(MaxInstrumentID)+1):
            # print(("abs instrument pos : " + str(InstrumentPos)))
            prev_instr = ""
            LayerCounter = 1
            for Instrument in range(len(SampleArray)):
                if SampleArray[Instrument][1] == InstrumentPos:
                    if not prev_instr == SampleArray[Instrument][1]:
                        print("- - - - - - - - - - - - - - - - - - - -")
                        print(("add instrument " +
                               str(SampleArray[Instrument][1]) +
                               " : " +
                               str(SampleArray[Instrument][3])))
                        AddInstrument(SampleArray[Instrument][1],
                                      SampleArray[Instrument][3])

                    # add layer to instrument
                    AddLayer(SampleArray[Instrument][0],
                             InstrumentLayersDct[InstrumentPos],
                             LayerCounter)
                    LayerCounter += 1

                    # close the instrument if this was the last layer
                    if (Instrument+1) < len(SampleArray):
                        arraythis = SampleArray[Instrument][1]
                        arraynext = SampleArray[Instrument+1][1]
                        if not arraythis == arraynext:
                            f.write('            </instrument>\n')
                    else:
                        f.write('            </instrument>\n')

                prev_instr = SampleArray[Instrument][1]

            # if there is no instrument with an instrument ID that matches
            # the current InstrumentPos, add a dummy instrument as placeholder
            # for this instrument position
            if InstrumentPos not in (foo[0] for foo in InstrumentLayers):
                AddInstrument(InstrumentPos, str(InstrumentPos))
                f.write('            </instrument>\n')

        f.write('    </instrumentList>\n')
        f.write('</drumkit_info>\n')
        f.close()

        # create tar file
        H2tarfile = DrumSetPath + DrumSetName + ".tar"
        tar = tarfile.open(H2tarfile, "w:gz")

        # check if the settings file + the info file are present
        if not os.path.isfile(DrumSetPath + "drumkit.xml"):
            return "drumkit.xml file not found in " + DrumSetPath

        # add drumkit.xml to tar
        tarinfo = tar.gettarinfo(DrumSetPath + "drumkit.xml",
                                 DrumSetName + "/drumkit.xml")
        tar.addfile(tarinfo, open(DrumSetPath + "drumkit.xml"))

        # add sample files to tar
        for i in range(len(SampleArray)):
            SampleToTar = SampleArray[i][0]
            # print "1 : " + SampleToTar
            tarinfo = tar.gettarinfo(DrumSetPath + "/" + SampleToTar,
                                     DrumSetName + "/" + SampleToTar)
            tar.addfile(tarinfo, open(DrumSetPath + SampleToTar))

        tar.close()

        # rename tar file to h2drumkit file
        os.rename(H2tarfile, DrumSetPath + DrumSetName + ".h2drumkit")
        print("- - - - - - - - - - - - - - - - - - - -")
        print(("Your Hydrogen drumkit file is available at " +
               DrumSetPath + DrumSetName + ".h2drumkit"))
        print()

    except IOError:
        return "Could not create drumkit.xml file " + filename

    return "OK"


if __name__ == "__main__":

    RetValue = "OK"

    RetValue = main()
    if not RetValue == "OK":
        print()
        print(RetValue)
        # Help()

    sys.exit(0)
