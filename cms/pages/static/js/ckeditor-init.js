window.onload = function() {

    let content_type = document.querySelector('#id_content_type').value
    if (content_type == 'html') {
        ClassicEditor.create(document.querySelector('#id_content'));
    }
    
    if (content_type == 'markdown') {
        ClassicEditor.create(document.querySelector('#id_content'));
    }

}
