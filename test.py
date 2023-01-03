from transformers.file_utils import cached_path, hf_bucket_url
import os, zipfile
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import soundfile as sf
import torch
import kenlm
from pyctcdecode import Alphabet, BeamSearchDecoderCTC, LanguageModel
import IPython
cache_dir = './cache/'
processor = Wav2Vec2Processor.from_pretrained("nguyenvulebinh/wav2vec2-base-vietnamese-250h", cache_dir=cache_dir)
model = Wav2Vec2ForCTC.from_pretrained("nguyenvulebinh/wav2vec2-base-vietnamese-250h", cache_dir=cache_dir)
lm_file = hf_bucket_url("nguyenvulebinh/wav2vec2-base-vietnamese-250h", filename='vi_lm_4grams.bin.zip')
lm_file = cached_path(lm_file,cache_dir=cache_dir)
with zipfile.ZipFile(lm_file, 'r') as zip_ref:
    zip_ref.extractall(cache_dir)
lm_file = cache_dir + 'vi_lm_4grams.bin'
def get_decoder_ngram_model(tokenizer, ngram_lm_path):
    vocab_dict = tokenizer.get_vocab()
    sort_vocab = sorted((value, key) for (key, value) in vocab_dict.items())
    vocab = [x[1] for x in sort_vocab][:-2]
    vocab_list = vocab
    # convert ctc blank character representation
    vocab_list[tokenizer.pad_token_id] = ""
    # replace special characters
    vocab_list[tokenizer.unk_token_id] = ""
    # vocab_list[tokenizer.bos_token_id] = ""
    # vocab_list[tokenizer.eos_token_id] = ""
    # convert space character representation
    vocab_list[tokenizer.word_delimiter_token_id] = " "
    # specify ctc blank char index, since conventially it is the last entry of the logit matrix
    alphabet = Alphabet.build_alphabet(vocab_list, ctc_token_idx=tokenizer.pad_token_id)
    lm_model = kenlm.Model(ngram_lm_path)
    decoder = BeamSearchDecoderCTC(alphabet,
                                   language_model=LanguageModel(lm_model))
    return decoder
ngram_lm_model = get_decoder_ngram_model(processor.tokenizer, lm_file)
# download test sound file
audio_file = hf_bucket_url("nguyenvulebinh/wav2vec2-base-vietnamese-250h", filename='audio-test/t1_utt000000042.wav')
audio_file = cached_path(audio_file,cache_dir=cache_dir)
os.rename(audio_file, cache_dir+"t1_utt000000042.wav")
audio_file = cache_dir+"t1_utt000000042.wav"
# define function to read in sound file
def map_to_array(batch):
    speech, sampling_rate = sf.read(batch["file"])
    batch["speech"] = speech
    batch["sampling_rate"] = sampling_rate
    return batch

# load dummy dataset and read soundfiles
ds = map_to_array({"file": audio_file})
# infer model
input_values = processor(
      ds["speech"],
      sampling_rate=ds["sampling_rate"],
      return_tensors="pt"
).input_values
# ).input_values.to("cuda")
# model.to("cuda")
logits = model(input_values).logits[0]
print(logits.shape)
# decode ctc output
pred_ids = torch.argmax(logits, dim=-1)
greedy_search_output = processor.decode(pred_ids)
beam_search_output = ngram_lm_model.decode(logits.cpu().detach().numpy(), beam_width=500)
print("Greedy search output: {}".format(greedy_search_output))
print("Beam search output: {}".format(beam_search_output))
IPython.display.Audio(filename=audio_file, autoplay=True)
