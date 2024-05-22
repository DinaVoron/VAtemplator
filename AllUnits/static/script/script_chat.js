const voice_start_btn = document.getElementById('voice-start');
const voice_stop_btn  = document.getElementById('voice-stop');
const send_btn        = document.getElementById('send');
const request_field   = document.getElementById('request');
let recognition;

//	function correct_text(text, language = 'ru') {
//	    const API_URL = 'https://languagetool.org/api/v2/check';
//		request_to_server(`${API_URL}?language=${language}&text=${encodeURIComponent(text)}`, 'GET', null, 'json', null)
//	    .then(data => {
//			if (data.matches && data.matches.length > 0) {
//				// Создаем исправленную версию текста, заменяя ошибки на предложенные исправления
//				let corrected_text = text;
//				data.matches.forEach(match => {
//					match.replacements.forEach(replacement => {
//						corrected_text = corrected_text.substring(0, match.offset) + replacement.value + corrected_text.substring(match.offset + match.length);
//					});
//				});
//				return corrected_text;
//			} else {
//				return text;
//			}
//	    })
//	    .catch(error => {
//	        console.error('Ошибка при отправке запроса на сервер:', error);
//			return text;
//	    });
//	}

voice_start_btn.addEventListener('click', () => {
	voice_start_btn.style.display = 'none';
	voice_stop_btn.style.display  = 'block';
	request_field.value           = '';

    recognition                = new webkitSpeechRecognition();
    recognition.continuous     = true;
    recognition.interimResults = true;
    recognition.lang           = 'ru-RU';

    let recognized_text = "";

    recognition.onresult = (event) => {
    	let interim_transcript = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
    		let transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                if (!transcript.endsWith('.')) {
                    transcript += '.';
                }
                recognized_text += transcript;
            } else {
                interim_transcript += transcript;
            }
        }

        request_field.value = recognized_text + interim_transcript;
    };

    recognition.start();
});

voice_stop_btn.addEventListener('click', () => {
	voice_start_btn.style.display = 'block';
	voice_stop_btn.style.display  = 'none';

    recognition.stop();
});

send_btn.addEventListener('click', () => {
	const chat = document.getElementById('chat');

	if (request_field.value == "") {
		return
	}

	request_to_server('/chat/send', 'POST', 'json', 'json', {
		scene:    chat.dataset.scene,
		question: request_field.value
	})
    .then(data => {
    	document.querySelector("article h1").innerHTML = "Чат :: " + data.scene_name;
    	chat.dataset.scene                             = data.scene_name;

    	let question         = document.createElement('div');
        question.textContent = data.question;
        question.classList.add('question');
        document.getElementById("chat-field").appendChild(question);

    	let answer           = document.createElement('div');
        answer.textContent   = data.answer;
        answer.classList.add('answer');
        document.getElementById("chat-field").appendChild(answer);

    	request_field.value = ""
    })
    .catch(error => {
        console.error('Ошибка при отправке запроса на сервер:', error);
    });
});

function end_dialog() {
	document.getElementById('end-dialog').style.display                = 'none';
	document.getElementById('end-dialog-successfully').style.display   = 'block';
	document.getElementById('end-dialog-unsuccessfully').style.display = 'block';

	voice_start_btn.style.display = 'block';
	voice_stop_btn.style.display  = 'none';
    recognition.stop();
}

function rating_dialog(rating) {
	document.getElementById('end-dialog').style.display                = 'block';
	document.getElementById('end-dialog-successfully').style.display   = 'none';
	document.getElementById('end-dialog-unsuccessfully').style.display = 'none';

	voice_start_btn.style.display = 'block';
	voice_stop_btn.style.display  = 'none';
    recognition.stop();

	request_to_server('/chat/rating', 'POST', 'text', 'json', rating)
    .then(data => {
    	document.querySelector("article h1").innerHTML = "Чат :: " + data.scene_name;
    	chat.dataset.scene                             = data.scene_name;

        document.getElementById("chat-field").innerHTML = '';

    	let message         = document.createElement('div');
        message.textContent = data.message;
        message.classList.add('answer');
        document.getElementById("chat-field").appendChild(message);

    	request_field.value = ""
    })
    .catch(error => {
        console.error('Ошибка при отправке запроса на сервер:', error);
    });
}
