import os
import pygame
from src import config

_inited = False
_bgm_tracks = {}
_sfx_cache = {}
_music_volume = config.DEFAULT_MUSIC_VOLUME
_sfx_volume = config.DEFAULT_SFX_VOLUME
_current_music = None


def init():
    global _inited
    if _inited:
        return
    if not config.AUDIO_ENABLED:
        if config.debug and config.debug_audio:
            print("[AUDIO] disabled by config")
        _inited = True
        return
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        _inited = True
        if config.debug and config.debug_audio:
            print("[AUDIO] mixer initialized")
    except pygame.error as e:
        if config.debug and config.debug_audio:
            print(f"[AUDIO] mixer init failed: {e}")


def load_all():
    if not _inited:
        return
    _load_bgm()


def _load_bgm():
    global _bgm_tracks
    _bgm_tracks = {}
    music_dir = config.MUSIC_DIR
    if not os.path.isdir(music_dir):
        if config.debug and config.debug_audio:
            print(f"[AUDIO] music dir not found: {music_dir}")
        return
    for entry in os.listdir(music_dir):
        if entry.lower().endswith((".mp3", ".ogg", ".wav")):
            name = os.path.splitext(entry)[0]
            path = os.path.join(music_dir, entry)
            _bgm_tracks[name] = path
            if config.debug and config.debug_audio:
                print(f"[AUDIO] registered BGM: {name} -> {path}")


def play_music(name, loops=-1):
    global _current_music
    if not _inited or not config.AUDIO_ENABLED:
        return
    if name not in _bgm_tracks:
        if config.debug and config.debug_audio:
            print(f"[AUDIO] BGM track not found: {name}")
        return
    if _current_music == name and pygame.mixer.music.get_busy():
        return
    try:
        pygame.mixer.music.load(_bgm_tracks[name])
        pygame.mixer.music.set_volume(_music_volume)
        pygame.mixer.music.play(loops=loops)
        _current_music = name
        if config.debug and config.debug_audio:
            print(f"[AUDIO] playing BGM: {name}")
    except pygame.error as e:
        if config.debug and config.debug_audio:
            print(f"[AUDIO] failed to play {name}: {e}")


def stop_music(fade_ms=500):
    global _current_music
    if not _inited or not config.AUDIO_ENABLED:
        return
    if fade_ms > 0:
        pygame.mixer.music.fadeout(fade_ms)
    else:
        pygame.mixer.music.stop()
    _current_music = None
    if config.debug and config.debug_audio:
        print("[AUDIO] music stopped")


def load_sfx(name, path):
    if not _inited or not config.AUDIO_ENABLED:
        return
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(_sfx_volume)
        _sfx_cache[name] = sound
        if config.debug and config.debug_audio:
            print(f"[AUDIO] loaded SFX: {name}")
    except pygame.error as e:
        if config.debug and config.debug_audio:
            print(f"[AUDIO] failed to load SFX {name}: {e}")


def play_sfx(name):
    if not _inited or not config.AUDIO_ENABLED:
        return
    if name not in _sfx_cache:
        if config.debug and config.debug_audio:
            print(f"[AUDIO] SFX not found: {name}")
        return
    _sfx_cache[name].play()


def set_music_volume(vol):
    global _music_volume
    _music_volume = max(0.0, min(1.0, vol))
    if _inited:
        pygame.mixer.music.set_volume(_music_volume)


def set_sfx_volume(vol):
    global _sfx_volume
    _sfx_volume = max(0.0, min(1.0, vol))
    for s in _sfx_cache.values():
        s.set_volume(_sfx_volume)


def get_music_volume():
    return _music_volume


def get_sfx_volume():
    return _sfx_volume


def is_playing():
    return _inited and pygame.mixer.music.get_busy()
