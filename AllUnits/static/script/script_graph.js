function event_update_directory() {
    var json_1 = [];
    var json_2 = [];

    request_to_server('/graph/update_document', 'GET', null, 'json', null)
    .then(data => {
        json_1 = data;
        return request_to_server('/graph/update_reference', 'GET', null, 'json', null);
    })
    .then(data => {
        json_2 = data;
        handleData();
    })
    .catch(error => console.error('Ошибка:', error));

    function handleData() {
        file_list = document.getElementById('document-list');
        file_list.innerHTML = '';

        let json_merged = [];
        if (json_1.length > 0 && json_2.length > 0) {
            json_merged = json_1.concat(json_2);
            json_merged = [...new Set(json_merged)];
        } else {
             if (json_1.length > 0) {
                json_merged = json_1;
             } else if (json_2.length > 0) {
                json_merged = json_2;
             } else {
                var item_list = document.createElement('li');
                item_list.textContent = 'Нет документов.';
                item_list.classList.add('file-item');
                file_list.appendChild(item_list);
                return;
             }
        }
        json_merged.sort();

        json_merged.forEach(function(item) {
            var item_list = document.createElement('li');
            item_list.classList.add('file-item');

            var item_p = document.createElement('p');
            var item_div_1 = document.createElement('div');
            var item_div_2 = document.createElement('div');

            item_p.textContent = item;

            if (json_1.includes(item)) {
                item_div_1.classList.add("elem-load");

                item_div_1.addEventListener('click', function() {
                    event_process_data(item);
                    swap_display("process-data");
                });
            }
            if (json_2.includes(item)) {
                item_div_2.classList.add("elem-delete");

                item_div_2.addEventListener('click', function() {
                    event_delete_data(item);
                });
            }

            item_list.appendChild(item_p);
            item_list.appendChild(item_div_1);
            item_list.appendChild(item_div_2);
            file_list.appendChild(item_list);
        });
    }
}

function event_upload_document() {
    if (document.getElementById('upload-document').files[0]) {
        var form = new FormData();
        form.append('document', document.getElementById('upload-document').files[0]);

        request_to_server('/graph/upload_document', 'POST', 'form', 'text', form)
        .then(data => {
            event_update_directory();
            console.log('Загрузка файла: ' + data);
        })
        .catch(error => console.error('Ошибка:', error));
    } else {
        console.error('Ошибка: Файл не выбран.');
    }
}


function event_visible_graph() {
    request_to_server('/graph/visible_data', 'GET', null, null, null)
    .then(() => {
        var iframe = document.querySelector("#graph-visible iframe");
        iframe.src = "/static/graph.html";
    })
    .catch(error => console.error('Ошибка:', error));
}



/* ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### */
/* Событие (Event) :: Обработка данных                                                                         */
/* ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### */
function event_process_data(filename) {
    request_to_server('/graph/process_data', 'POST', 'text', 'json', filename)
    .then(data => {
        document.getElementById('content-container').innerHTML = data.content_html;
        document.getElementById('cluster-container').innerHTML = data.clusters_html;
        bind_functions_table();
    })
    .catch(error => console.error('Ошибка:', error));
}

/* ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### */
/* Событие (Event) :: Обработка данных :: Вспомогательные функции                                              */
/* ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### */
function bind_functions_table() {
	const table = document.querySelector("#cluster-container table");
	if (!table) return;

	let dragged_elm = null;

	const elms  = table.querySelectorAll('td div');
    elms.forEach(elm => {
        elm.draggable = true;

        elm.addEventListener('dragstart', () => {
            dragged_elm = elm;
            elm.classList.add('dragging');
        });
        elm.addEventListener('dragend', () => {
            dragged_elm = null;
            elm.classList.remove('dragging');
        });
    });

	const cells = table.querySelectorAll('td');
	cells.forEach(cell => {
        cell.addEventListener('dragover', (event) => {
            event.preventDefault();
        });

		cell.addEventListener('drop', (event) => {
			if (dragged_elm) {
				const row_src  = dragged_elm.parentNode;
				const row_dest = cell;
				const elm      = dragged_elm;

				if (row_src !== row_dest) {
					request_to_server('/graph/process_data/draggable_cluster', 'POST', 'json', 'json', {
						index_list_src:  JSON.parse(row_src.parentNode.getAttribute('data-cluster')),
						index_list_dest: JSON.parse(row_dest.parentNode.getAttribute('data-cluster')),
						index:           Array.from(row_src.children).indexOf(elm)
					})
                    .then(data => {
                        if (data.flag) {
							document.getElementById('content-container').innerHTML = data.content_html;
							document.getElementById('cluster-container').innerHTML = data.clusters_html;
							bind_functions_table();
                        }
                    })
                    .catch(error => {
                        console.error('Ошибка при отправке запроса на сервер:', error);
                    });
				}
			}
		});
	});
}

function change_cluster_name(name_last, name_next, lemma) {
	request_to_server('/graph/process_data/change_cluster_name', 'POST', 'json', 'json', {
		lemma: lemma, name_last: name_last, name_next: name_next
	})
    .then(data => {
        document.getElementById('content-container').innerHTML = data.content_html;
        document.getElementById('cluster-container').innerHTML = data.clusters_html;
        bind_functions_table();
    })
    .catch(error => console.error('Ошибка:', error));
}

function change_cluster_flag(flag, element) {
	request_to_server('/graph/process_data/change_cluster_flag', 'POST', 'json', 'json', {
		flag: flag, index_list: JSON.parse(element.parentNode.getAttribute('data-cluster'))
	})
    .then(data => {
        document.getElementById('content-container').innerHTML = data.content_html;
        document.getElementById('cluster-container').innerHTML = data.clusters_html;
        bind_functions_table();
    })
    .catch(error => console.error('Ошибка:', error));
}

function select_cluster(element) {
    request_to_server('/graph/process_data/select_cluster', 'POST', 'json', 'json', {
    	index_list: JSON.parse(element.getAttribute('data-cluster'))
    })
    .then(data => {
        document.getElementById('content-container').innerHTML = data.content_html;
        document.getElementById('cluster-container').innerHTML = data.clusters_html;
        bind_functions_table();
    })
    .catch(error => console.error('Ошибка:', error));
}



/* ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### */
/* Событие (Event) :: Загрузка данных                                                                          */
/* ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### */
function event_load_data() {
	request_to_server('/graph/load_data', 'GET', null, null, null)
    .then(response => {
        event_update_directory();
        event_cancel();
    })
    .catch(error => console.error('Ошибка:', error));
}



/* ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### */
/* Событие (Event) :: Удаление данных                                                                          */
/* ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### */
function event_delete_data(filename) {
	request_to_server('/graph/delete_data', 'POST', 'text', null, filename)
    .then(response => {
        event_update_directory();
    })
    .catch(error => console.error('Ошибка:', error));
}







//function element() {
//    fetch('/graph/process_data_select')
//    .then(response => response.json())
//    .then(data => {
//        document.getElementById('content-container').innerHTML = data.content_html;
//        document.getElementById('cluster-container').innerHTML = data.clusters_html;
//    })
//    .catch(error => console.error('Ошибка:', error));
//}








function event_cancel() {
    swap_display('graph-visible');
    // clear_table();
}




function swap_display(display) {
    if (display === "graph-visible") {
    	document.querySelector("article").style.display = "block";
    	document.querySelector("aside").style.width = "calc(var(--graph-width_aside) - 2 * var(--margin_m))";

        document.getElementById("graph-visible").style.display = "flex";
        document.getElementById("process-data").style.display =  "none";
    } else {
    	document.querySelector("article").style.display = "none";
    	document.querySelector("aside").style.width = "calc(var(--graph-width_aside) - 2 * var(--margin_m) + var(--graph-width_article))";

        document.getElementById("graph-visible").style.display = "none";
        document.getElementById("process-data").style.display =  "flex";
    }
}
