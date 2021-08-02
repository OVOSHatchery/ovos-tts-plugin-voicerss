# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from ovos_plugin_manager.templates.tts import TTS, TTSValidator
import requests


class VoiceRSSTTSPlugin(TTS):
    """Interface to voicerss TTS."""
    supported_langs = {"ca-es": ["Catalan"],
                       "zh-cn": ["Chinese (China)"],
                       "zh-hk": ["Chinese (Hong Kong)"],
                       "zh-tw": ["Chinese (Taiwan)"],
                       "da-dk": ["Danish"],
                       "nl-nl": ["Dutch"],
                       "en-au": ["English (Australia)"],
                       "en-ca": ["English (Canada)"],
                       "en-gb": ["English (Great Britain)"],
                       "en-in": ["English (India)"],
                       "en-us": ["English (United States)"],
                       "fi-fi": ["Finnish"],
                       "fr-ca": ["French (Canada)"],
                       "fr-fr": ["French (France)"],
                       "de-de": ["German"],
                       "it-it": ["Italian"],
                       "ja-jp": ["Japanese"],
                       "ko-kr": ["Korean"],
                       "nb-no": ["Norwegian"],
                       "pl-pl": ["Polish"],
                       "pt-br": ["Portuguese (Brazil)"],
                       "pt-pt": ["Portuguese (Portugal)"],
                       "ru-ru": ["Russian"],
                       "es-mx": ["Spanish (Mexico)"],
                       "es-es": ["Spanish (Spain)"],
                       "sv-se": ["Swedish (Sweden)"]}

    def __init__(self, lang="en-us", config=None):
        super(VoiceRSSTTSPlugin, self).__init__(
            lang, config, VoiceRSSTTSValidator(self), 'mp3')
        self.key = self.config.get("key")
        self.voice = self.voice.get("voice")
        self.rate = self.voice.get("speed", 0)

    def get_tts(self, sentence, wav_file):
        with open(wav_file, "wb") as f:
            f.write(self._request(sentence))
        return wav_file, None

    def _request(self, sentence):
        params = {
            'key': self.key,
            'hl': self.lang,
            'src': sentence,
            'r': str(self.rate),
            'c': "mp3",
            'f': '44khz_16bit_stereo',
            'ssml': 'false',
            'b64': 'false'
        }
        if self.voice:
            params["v"] = self.voice

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}

        url = "https://api.voicerss.org:443"
        response = requests.post(url, '/', params=params, headers=headers)

        content = response.text

        if response.status_code != 200:
            error = response.reason
        elif content.find('ERROR') == 0:
            error = content
        else:
            return bytes(response.content)

        raise RuntimeError(error)


class VoiceRSSTTSValidator(TTSValidator):
    def __init__(self, tts):
        super(VoiceRSSTTSValidator, self).__init__(tts)

    def validate_lang(self):
        lang = self.tts.lang
        assert lang in VoiceRSSTTSPlugin.supported_langs

    def validate_connection(self):
        # TODO check that server is up
        assert self.tts.key is not None

    def get_tts_class(self):
        return VoiceRSSTTSPlugin
