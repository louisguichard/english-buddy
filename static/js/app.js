document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const speakButton = document.getElementById('speak-button');
    const userTextElement = document.getElementById('user-text');
    const assistantTextElement = document.getElementById('assistant-text');
    const definitionContainer = document.getElementById('word-definition');
    const definitionWord = document.querySelector('.definition-word');
    const definitionText = document.querySelector('.definition-text');
    const replayUserButton = document.getElementById('replay-user');
    const replayAssistantButton = document.getElementById('replay-assistant');
    const rephraseUserButton = document.getElementById('rephrase-user');
    const rephrasedTextContainer = document.getElementById('rephrased-text');
    
    // Save the current and previous AI responses for context
    let currentAiResponse = '';
    let previousAiResponse = '';
    
    // Save the user's speech for replay
    let currentUserSpeech = '';
    
    // Cache for word definitions to avoid redundant API calls
    let definitionsCache = {};
    
    // MediaRecorder variables
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    
    // Initialize the application
    initApp();
    
    function initApp() {
        // Set up button click handler
        speakButton.addEventListener('click', toggleRecording);
        
        // Set up definition container click to dismiss it
        definitionContainer.addEventListener('click', function() {
            definitionContainer.classList.remove('visible');
        });
        
        // Set up replay buttons click handlers
        replayUserButton.addEventListener('click', replayUserMessage);
        replayAssistantButton.addEventListener('click', replayAssistantMessage);
        
        // Set up rephrase button click handler
        rephraseUserButton.addEventListener('click', requestRephrase);
        
        // Set up rephrased text container click to dismiss it
        rephrasedTextContainer.addEventListener('click', function() {
            rephrasedTextContainer.classList.remove('visible');
        });
        
        // Initialize button style
        speakButton.classList.add('btn-start');
    }
    
    async function toggleRecording() {
        if (!isRecording) {
            // Start recording
            startRecording();
        } else {
            // Stop recording
            stopRecording();
        }
    }
    
    async function startRecording() {
        try {
            // Request access to the microphone
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Clear only the user text, keep assistant text
            userTextElement.innerHTML = '';
            
            // Hide word definition container
            definitionContainer.classList.remove('visible');
            
            // Hide rephrased text container
            rephrasedTextContainer.classList.remove('visible');
            rephrasedTextContainer.innerHTML = '';
            
            // Create media recorder
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            // Collect audio data
            mediaRecorder.addEventListener('dataavailable', event => {
                audioChunks.push(event.data);
            });
            
            // Start recording
            mediaRecorder.start();
            isRecording = true;
            
            // Update button text and style
            speakButton.textContent = 'Stop';
            speakButton.classList.remove('btn-start');
            speakButton.classList.add('btn-stop');
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Error accessing microphone. Please ensure you have allowed microphone access.');
        }
    }
    
    function stopRecording() {
        if (!mediaRecorder) return;
        
        // Before clearing, save the current AI response as previous
        previousAiResponse = currentAiResponse;
        
        // Clear assistant text when stopping the recording
        assistantTextElement.innerHTML = '';
        
        // Update state and button text
        isRecording = false;
        speakButton.textContent = 'Processing...';
        speakButton.disabled = true;
        speakButton.classList.remove('btn-stop');
        speakButton.classList.add('btn-processing');
        
        // Stop recording
        mediaRecorder.addEventListener('stop', processAudio);
        mediaRecorder.stop();
        
        // Stop all microphone tracks
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
    
    async function processAudio() {
        try {
            // Create audio blob and convert to base64
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const reader = new FileReader();
            
            reader.onload = async function(event) {
                const audioBase64 = event.target.result;
                await processAudioInSteps(audioBase64);
            };
            
            reader.readAsDataURL(audioBlob);
            
        } catch (error) {
            console.error('Error processing audio:', error);
            resetButton();
        }
    }
    
    async function processAudioInSteps(audioData) {
        try {
            // Step 1: Get transcription first
            const transcriptionResponse = await fetch('/api/process-audio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ audio: audioData })
            });
            
            if (!transcriptionResponse.ok) {
                throw new Error('Server error during transcription');
            }
            
            const transcriptionData = await transcriptionResponse.json();
            
            // Store the user's transcription for replay
            currentUserSpeech = transcriptionData.transcription;
            
            // Display transcription with mispronounced words in red
            displayTranscription(transcriptionData.transcription, transcriptionData.words);
            
            // Step 2: Generate response - only send the transcription text, not the word confidence data
            const responseResponse = await fetch('/api/generate-response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    transcription: transcriptionData.transcription 
                })
            });
            
            if (!responseResponse.ok) {
                throw new Error('Server error during response generation');
            }
            
            const responseData = await responseResponse.json();
            
            // Display assistant response
            displayAssistantResponse(responseData.response);
            
            // Reset button
            resetButton();
            
        } catch (error) {
            console.error('Error processing speech:', error);
            alert('Error processing your speech. Please try again.');
            resetButton();
        }
    }
    
    function resetButton() {
        speakButton.textContent = 'Speak';
        speakButton.disabled = false;
        speakButton.classList.remove('btn-stop', 'btn-processing');
        speakButton.classList.add('btn-start');
    }
    
    function displayTranscription(text, words) {
        if (!text) return;
        
        // Create a mapping of whisper words for easier lookup
        const whisperWords = {};
        words.forEach(wordInfo => {
            whisperWords[wordInfo.position] = {
                word: wordInfo.word,
                is_low_confidence: wordInfo.is_low_confidence,
                position: wordInfo.position
            };
        });
        
        // Convert text to HTML with clickable spans
        let wordIndex = 0;
        let htmlText = '';
        let wordBuffer = '';
        let inWord = false;
        
        // Process each character to create word spans
        for (let i = 0; i < text.length; i++) {
            const char = text[i];
            
            // Check if character is part of a word (including apostrophes within words)
            const isWordChar = /[\w']/.test(char) && 
                              !(char === "'" && (!inWord || i === text.length - 1 || !/\w/.test(text[i+1])));
            
            if (isWordChar) {
                // Start or continue a word
                wordBuffer += char;
                inWord = true;
            } else {
                // End of word
                if (inWord && wordBuffer.length > 0) {
                    // Check if this word exists in the whisper words and create span accordingly
                    if (whisperWords[wordIndex]) {
                        const wordInfo = whisperWords[wordIndex];
                        const spanClass = wordInfo.is_low_confidence ? 'user-word red-text' : 'user-word';
                        htmlText += `<span class="${spanClass}" data-position="${wordInfo.position}">${wordBuffer}</span>`;
                    } else {
                        htmlText += `<span class="user-word" data-position="${wordIndex}">${wordBuffer}</span>`;
                    }
                    wordIndex++;
                    wordBuffer = '';
                    inWord = false;
                }
                
                // Add the non-word character as is
                htmlText += char;
            }
        }
        
        // Add any remaining word
        if (wordBuffer.length > 0) {
            if (whisperWords[wordIndex]) {
                const wordInfo = whisperWords[wordIndex];
                const spanClass = wordInfo.is_low_confidence ? 'user-word red-text' : 'user-word';
                htmlText += `<span class="${spanClass}" data-position="${wordInfo.position}">${wordBuffer}</span>`;
            } else {
                htmlText += `<span class="user-word" data-position="${wordIndex}">${wordBuffer}</span>`;
            }
        }
        
        userTextElement.innerHTML = htmlText;
        
        // Add click event listeners to all words
        document.querySelectorAll('.user-word').forEach(wordElem => {
            wordElem.addEventListener('click', function() {
                const position = parseInt(this.getAttribute('data-position'));
                playUserWord(position);
            });
        });
    }
    
    function displayAssistantResponse(text) {
        if (!text) return;
        
        // Save the response for context in definitions
        currentAiResponse = text;
        
        // Clear definitions cache when a new response is displayed
        definitionsCache = {};
        
        // Process text character by character to properly handle contractions
        let htmlText = '';
        let wordBuffer = '';
        let inWord = false;
        
        // Process each character to create word spans
        for (let i = 0; i < text.length; i++) {
            const char = text[i];
            
            // Check if character is part of a word (including apostrophes within words)
            const isWordChar = /[\w']/.test(char) && 
                              !(char === "'" && (!inWord || i === text.length - 1 || !/\w/.test(text[i+1])));
            
            if (isWordChar) {
                // Start or continue a word
                wordBuffer += char;
                inWord = true;
            } else {
                // End of word
                if (inWord && wordBuffer.length > 0) {
                    // Add the clickable word span
                    htmlText += `<span class="ai-word">${wordBuffer}</span>`;
                    wordBuffer = '';
                    inWord = false;
                }
                
                // Add the non-word character as is
                htmlText += char;
            }
        }
        
        // Add any remaining word
        if (wordBuffer.length > 0) {
            htmlText += `<span class="ai-word">${wordBuffer}</span>`;
        }
        
        assistantTextElement.innerHTML = htmlText;
        
        // Add click event listeners to all AI words
        document.querySelectorAll('.ai-word').forEach(wordElem => {
            wordElem.addEventListener('click', function() {
                const word = this.textContent;
                playAiWord(word);
            });
        });
    }
    
    async function playUserWord(position) {
        try {
            // Request the server to play this specific word
            const response = await fetch('/api/play-user-word', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    wordInfo: { position: position } 
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to play word');
            }
            
            const data = await response.json();
            
            if (data.success && data.word_segment) {
                // We got the timing information for the word
                // Play the specific segment from the recording
                playAudioSegment('temp_recording.wav', data.word_segment.start, data.word_segment.end);
            }
        } catch (error) {
            console.error('Error playing user word:', error);
        }
    }
    
    async function playAiWord(word) {
        try {
            // Show definition container immediately
            definitionContainer.classList.add('visible');
            definitionWord.textContent = word.charAt(0).toUpperCase() + word.slice(1);
            
            // Check if we already have this definition in the cache and display it immediately
            if (definitionsCache[word]) {
                definitionText.textContent = " - " + definitionsCache[word];
            } else {
                definitionText.innerHTML = '<span class="definition-loading"> - Loading definition...</span>';
            }
            
            // Request the server to synthesize and play this word (don't await)
            fetch('/api/play-ai-word', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ word: word })
            }).catch(error => {
                console.error('Error playing AI word:', error);
            });
            
            // Only fetch the definition if it's not already cached
            if (!definitionsCache[word]) {
                const defResponse = await fetch('/api/get-word-definition', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 
                        word: word,
                        context: currentAiResponse
                    })
                });
                
                if (!defResponse.ok) {
                    throw new Error('Failed to get word definition');
                }
                
                const defData = await defResponse.json();
                definitionText.textContent = " - " + defData.definition;
                
                // Save to cache
                definitionsCache[word] = defData.definition;
            }
        } catch (error) {
            console.error('Error getting word definition:', error);
            definitionText.textContent = 'Definition not available';
        }
    }
    
    async function requestRephrase() {
        try {
            // Only attempt to rephrase if we have user text
            if (!currentUserSpeech) {
                console.log('No user speech to rephrase');
                return;
            }
            
            // Show loading state
            rephraseUserButton.disabled = true;
            rephrasedTextContainer.classList.add('visible');
            rephrasedTextContainer.innerHTML = '<span class="rephrased-loading">Getting rephrasing suggestions...</span>';
            
            // Request rephrasing from the server
            // Use previousAiResponse for context, not currentAiResponse
            const response = await fetch('/api/rephrase-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    text: currentUserSpeech,
                    last_ai_response: previousAiResponse
                })
            });
            
            if (!response.ok) {
                throw new Error('Server error during rephrasing');
            }
            
            const data = await response.json();
            
            // Display the result
            if (data.needs_rephrasing && data.rephrased_text) {
                // Show the rephrased text
                rephrasedTextContainer.textContent = data.rephrased_text;
                rephrasedTextContainer.classList.add('visible');
            } else {
                // Show a success message
                rephrasedTextContainer.textContent = 'Your sentence was already well-formed! Good job!';
                rephrasedTextContainer.classList.add('visible');
            }
            
            // Re-enable the button
            rephraseUserButton.disabled = false;
            
        } catch (error) {
            console.error('Error getting rephrasing:', error);
            rephrasedTextContainer.innerHTML = '<span class="rephrased-loading">Could not get rephrasing suggestions. Please try again.</span>';
            rephrasedTextContainer.classList.add('visible');
            rephraseUserButton.disabled = false;
        }
    }
    
    function playAudioSegment(audioFile, startTime, endTime) {
        // Create an audio element to play the segment
        const audio = new Audio();
        audio.src = '/' + audioFile;  // Make sure we have the correct path
        
        audio.addEventListener('loadedmetadata', () => {
            // When loaded, set the current time to the start time
            audio.currentTime = startTime;
            
            // Start playing
            audio.play();
            
            // Stop after the segment duration
            const duration = endTime - startTime;
            setTimeout(() => {
                audio.pause();
            }, duration * 1000); // Convert to milliseconds
        });
        
        audio.addEventListener('error', (e) => {
            console.error('Error loading audio:', e);
        });
    }
    
    // Function to replay the entire user message
    function replayUserMessage() {
        if (!currentUserSpeech) {
            console.log('No user speech to replay');
            return;
        }
        
        // Create an audio element to play the full recording
        const audio = new Audio();
        audio.src = '/temp_recording.wav';  // Use the original recording
        audio.play();
    }
    
    // Function to replay the entire assistant message
    function replayAssistantMessage() {
        if (!currentAiResponse) {
            console.log('No assistant response to replay');
            return;
        }
        
        fetch('/api/play-ai-word', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ word: currentAiResponse })
        }).catch(error => {
            console.error('Error replaying assistant message:', error);
        });
    }
}); 