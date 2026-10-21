#!/bin/sh
# Re-link the local-STT dependency closure from the `pm` env into the gateway venv.
# Non-overwriting: existing packages in the target are left untouched.
set -eu

SRC=/opt/data/installs/351f81cc06284494/environments/16a9730ab2b54b5681bde23289dfcf3e/venv
DST=/opt/hermes/.venv

SRC_SP=$(ls -d "$SRC"/lib/python*/site-packages)
DST_SP=$(ls -d "$DST"/lib/python*/site-packages)
echo "src=$SRC_SP"
echo "dst=$DST_SP"

for name in \
    faster_whisper ctranslate2 ctranslate2.libs onnxruntime \
    flatbuffers av av.libs huggingface_hub hf_xet tokenizers \
    numpy numpy.libs filelock fsspec tqdm yaml
do
    matched=0
    for p in "$SRC_SP/$name" "$SRC_SP/$name".dist-info "$SRC_SP/$name"-*.dist-info; do
        [ -e "$p" ] || continue
        b=$(basename "$p")
        if [ -e "$DST_SP/$b" ]; then
            echo "skip (exists): $b"
        else
            cp -a "$p" "$DST_SP/$b"
            echo "linked: $b"
        fi
        matched=1
    done
    [ "$matched" -eq 1 ] || echo "WARN not found in src: $name"
done

echo "--- verify ---"
"$DST/bin/python" -c "import faster_whisper, ctranslate2, av, onnxruntime; print('STT imports OK')"
