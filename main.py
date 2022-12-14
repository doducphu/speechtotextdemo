import vosk
import json
import queue
import sounddevice as sd
import time
import manual as cont


conf_device = None
conf_model_path = "./model"
conf_samplerate = int(sd.query_devices(None, "input")["default_samplerate"])

model = vosk.Model(conf_model_path)
q = queue.Queue()
# hih
def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

cont.main()

repeat = []
print("Init voice recognition")
with sd.RawInputStream(samplerate=conf_samplerate, device=conf_device, blocksize=8000, channels=1, callback=callback, dtype='int16'):
    rec = vosk.KaldiRecognizer(model, conf_samplerate)
    while True:
        data = q.get()
        if (rec.AcceptWaveform(data)):
            output = json.loads(rec.Result())["text"]
            print(output)
            o = output
            for output in o.split(" "):
                if (output != ""):
                    #print(output)
                    if (output == "ah" and len(repeat) > 0):
                        if(cont.handle_voice(repeat[-1])):
                            repeat.append(repeat[-1])
                            print("Repeating action")
                            print(repeat[-1])
                    elif (output != "repeat"):
                        if (cont.handle_voice(output)):
                            repeat.append(output)
                            time.sleep(2)
                    else:
                        for n in range(len(repeat)):
                            cont.handle_voice(repeat[n])
                            time.sleep(2)
                        repeat = []