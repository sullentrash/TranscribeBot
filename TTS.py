import os

class TTS:
    """
    Класс для преобразования текста в аудио.
    Поддерживаются форматы аудио: wav, ogg
    """
    default_init = {
        "sample_rate": 24000,
        "device_init": "cpu",
        "threads": 4,
        "speaker_voice": "kseniya",
        "model_path": "models/silero/model.pt",  # путь к файлу TTS модели Silero
        "model_url": "https://models.silero.ai/models/tts/ru/v3_1_ru.pt", # URL к TTS модели Silero
        "ffmpeg_path": "models/silero"  # путь к ffmpeg
    }

    def __init__(
        self,
        sample_rate=None,
        device_init=None,
        threads=None,
        speaker_voice=None,
        model_path=None,
        model_url=None,
        ffmpeg_path=None
    ) -> None:
        """
        Настройка модели Silero для преобразования текста в аудио.

        :arg sample_rate: int       # 8000, 24000, 48000 - качество звука
        :arg device_init: str       # "cpu", "gpu"(для gpu нужно ставить другой torch)
        :arg threads: int           # количество тредов, например, 4
        :arg speaker_voice: str     # диктор "aidar", "baya", "kseniya", "xenia", "random"(генерит голос каждый раз, долго)
        :arg model_path: str        # путь до модели silero
        :arg model_url: str         # URL к TTS модели Silero
        :arg ffmpeg_path: str       # путь к ffmpeg
        """
        self.sample_rate = sample_rate if sample_rate else TTS.default_init["sample_rate"]
        self.device_init = device_init if device_init else TTS.default_init["device_init"]
        self.threads = threads if threads else TTS.default_init["threads"]
        self.speaker_voice = speaker_voice if speaker_voice else TTS.default_init["speaker_voice"]
        self.model_path = model_path if model_path else TTS.default_init["model_path"]
        self.model_url = model_url if model_url else TTS.default_init["model_url"]
        self.ffmpeg_path = ffmpeg_path if ffmpeg_path else TTS.default_init["ffmpeg_path"]

        self._check_model()

        device = torch.device(self.device_init)
        torch.set_num_threads(self.threads)
        self.model = torch.package.PackageImporter(self.model_path).load_pickle("tts_models", "model")
        self.model.to(device)

    def _get_wav(self, text: str, speaker_voice=None, sample_rate=None) -> str:
        """
        Конвертирует текст в wav файл

        :arg text:  str  # текст до 1000 символов
        :arg speaker_voice:  str  # голос диктора
        :arg sample_rate: str  # качество выходного аудио
        :return: str  # путь до выходного файла
        """
        if text is None:
            raise Exception("Передайте текст")

        # Удаляем существующий файл чтобы все хорошо работало
        if os.path.exists("test.wav"):
            os.remove("test.wav")

        if speaker_voice is None:
            speaker_voice = self.speaker_voice

        if sample_rate is None:
            sample_rate = self.sample_rate

        # Сохранение результата в файл test.wav
        return self.model.save_wav(
            text=text,
            speaker=speaker_voice,
            sample_rate=sample_rate
        )

    def text_to_ogg(self, text: str, out_filename: str = None) -> str:
        """
        Конвертирует текст в файл ogg.
        Модель игнорирует латиницу, но поддерживает цифры числами.

        :arg text: str  # текст кирилицей
        :return: str    # имя выходного файла
        """
        if text is None:
            raise Exception("Передайте текст")

        # Делаем числа буквами
        text = self._nums_to_text(text)

        # Генерируем ogg если текст < 1000 символов
        if len(text) < 1000:
            # Возвращаем путь до ogg
            ogg_audio_path = self._get_ogg(text)

            if out_filename is None:
                return ogg_audio_path

            return self._rename_file(ogg_audio_path, out_filename)

        # Разбиваем текст, конвертируем и склеиваем аудио в один файл
        texts = [text[x:x+990] for x in range(0, len(text), 990)]
        files = []
        for index in range(len(texts)):
            # Конвертируем текст в ogg, возвращаем путь до ogg
            ogg_audio_path = self._get_ogg(texts[index])
            # Переименовываем чтобы не затереть файл
            new_ogg_audio_path = f"{index}_{ogg_audio_path}"
            os.rename(ogg_audio_path, new_ogg_audio_path)
            # Добавляем новый файл в список
            files.append(new_ogg_audio_path)

        # Склеиваем все ogg файлы в один
        ogg_audio_path = self._merge_audio_n_to_1(files, out_filename="test_n_1.ogg")
        # Удаляем временные файлы
        [os.remove(file) for file in files]

        if out_filename is None:
            return ogg_audio_path

        return self._rename_file(ogg_audio_path, out_filename)