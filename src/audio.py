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
    """Initialise the pygame mixer for audio playback."""
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
    """Load all audio assets (background music tracks)."""
    if not _inited:
        return
    _load_bgm()


def _load_bgm():
    """Scan the music directory and register all BGM tracks."""
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


def play_music_file(path, loops=-1):
    """Play a music file, skipping if already the current track."""
    global _current_music
    if not _inited or not config.AUDIO_ENABLED:
        return
    if not os.path.isfile(path):
        if config.debug and config.debug_audio:
            print(f"[AUDIO] music file not found: {path}")
        return
    if _current_music == path and pygame.mixer.music.get_busy():
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(_music_volume)
        pygame.mixer.music.play(loops=loops)
        _current_music = path
        if config.debug and config.debug_audio:
            print(f"[AUDIO] playing BGM from: {path}")
    except pygame.error as e:
        if config.debug and config.debug_audio:
            print(f"[AUDIO] failed to play {path}: {e}")


def stop_music(fade_ms=500):
    """Stop the currently playing music with an optional fade-out."""
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


def set_music_volume(vol):
    """Set the music volume, clamped to [0.0, 1.0]."""
    global _music_volume
    _music_volume = max(0.0, min(1.0, vol))
    if _inited:
        pygame.mixer.music.set_volume(_music_volume)


def set_sfx_volume(vol):
    """Set the SFX volume, clamped to [0.0, 1.0]."""
    global _sfx_volume
    _sfx_volume = max(0.0, min(1.0, vol))
    for s in _sfx_cache.values():
        s.set_volume(_sfx_volume)


def get_music_volume():
    """Return the current music volume level."""
    return _music_volume


def get_sfx_volume():
    """Return the current SFX volume level."""
    return _sfx_volume


def get_debug_info():
    """Return a debug string summarising the audio state."""
    return (f"[AUDIO] enabled={config.AUDIO_ENABLED} "
            f"music={'playing' if _inited and pygame.mixer.music.get_busy() else 'stopped'} "
            f"sfx_cached={len(_sfx_cache)}")
