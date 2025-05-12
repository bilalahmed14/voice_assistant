document.addEventListener('DOMContentLoaded', () => {
    const recordButton = document.getElementById('recordButton');
    const status = document.getElementById('status');
    const questionDiv = document.getElementById('question');
    const answerDiv = document.getElementById('answer');
    let mediaRecorder;
    let audioChunks = [];

    // Check if browser supports media recording
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        status.textContent = 'Your browser does not support audio recording';
        recordButton.disabled = true;
        return;
    }

    recordButton.addEventListener('click', async () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            // Stop recording
            mediaRecorder.stop();
            recordButton.classList.remove('recording');
            status.textContent = 'Processing...';
        } else {
            // Start recording
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream, {
                    mimeType: 'audio/webm;codecs=opus'
                });
                audioChunks = [];

                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm;codecs=opus' });
                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'recording.webm');

                    try {
                        const response = await fetch('/process_voice', {
                            method: 'POST',
                            body: formData
                        });

                        const data = await response.json();
                        
                        if (data.success) {
                            // Display question
                            questionDiv.classList.remove('hidden');
                            questionDiv.classList.add('show');
                            questionDiv.querySelector('p').textContent = data.question;

                            // Display answer
                            answerDiv.classList.remove('hidden');
                            answerDiv.classList.add('show');
                            answerDiv.querySelector('p').textContent = data.answer;

                            // Play audio response
                            const audio = new Audio(data.audio_url);
                            audio.play();

                            status.textContent = 'Ready';
                        } else {
                            status.textContent = `Error: ${data.error}`;
                        }
                    } catch (error) {
                        status.textContent = `Error: ${error.message}`;
                    }
                };

                mediaRecorder.start();
                recordButton.classList.add('recording');
                status.textContent = 'Recording...';
            } catch (error) {
                status.textContent = `Error: ${error.message}`;
            }
        }
    });
}); 