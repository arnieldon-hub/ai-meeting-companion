import gradio as gr
from transformers import pipeline

print("Loading Whisper model...")
asr = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-tiny.en"
)

print("Loading summary model...")
summary_model = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

print("Models loaded!")


def extract_key_points(transcript: str) -> str:
    sentences = [s.strip() for s in transcript.split(".") if s.strip()]

    bullets = []

    for sentence in sentences:
        lower = sentence.lower()

        if any(word in lower for word in [
            "test", "meeting", "plan", "decide", "decision",
            "action", "next step", "deadline", "project",
            "summary", "discuss", "assessment", "accuracy"
        ]):
            bullets.append(f"- {sentence}.")

    if not bullets:
        bullets = [f"- {sentence}." for sentence in sentences[:3]]

    return "\n".join(bullets[:5])


def process_meeting(audio_file):
    if audio_file is None:
        return "Please upload an audio file.", "", ""

    transcript = asr(audio_file)["text"].strip()

    if not transcript:
        return "No transcript could be generated.", "", ""

    summary = summary_model(
        transcript,
        max_length=60,
        min_length=20,
        do_sample=False
    )[0]["summary_text"].strip()

    key_points = extract_key_points(transcript)

    return transcript, summary, key_points


with gr.Blocks(title="Business AI Meeting Companion") as app:
    gr.Markdown("# 🧠 Business AI Meeting Companion")
    gr.Markdown(
        "Upload meeting audio to generate a transcript, summary, and key points."
    )

    audio_input = gr.Audio(
        sources="upload",
        type="filepath",
        label="Upload Meeting Audio"
    )

    transcript_output = gr.Textbox(label="Transcript", lines=8)
    summary_output = gr.Textbox(label="Summary", lines=4)
    keypoints_output = gr.Textbox(label="Key Points", lines=6)

    process_button = gr.Button("Process Meeting")

    process_button.click(
        fn=process_meeting,
        inputs=audio_input,
        outputs=[transcript_output, summary_output, keypoints_output]
    )

app.launch()
