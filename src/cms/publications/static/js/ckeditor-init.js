/*
 * build your editor
 * https://ckeditor.com/ckeditor-5/online-builder/
 * 
 * list all available plugins
 * ClassicEditor.builtinPlugins.map( plugin => plugin.pluginName );
 * 
 * 
 */


// load ckfinder js
const script = document.createElement('script')
script.src = 'https://ckeditor.com/apps/ckfinder/3.5.0/ckfinder.js';
document.head.append(script)


window.onload = function() {
    
    let content_type = document.querySelector('#id_content_type').value;
    ClassicEditor.defaultConfig = {
        toolbar: {
            
            items: [
                'heading', '|',
                //'alignment', '|',
                'bold', 'italic', 'strikethrough', 'underline', 'removeformat', '|',
                'blockQuote', 'codeBlock', '|',
                'outdent', 'indent', '|',
                'imageInsert', 'ckfinder', 'link', 'horizontalLine', '|',
                'bulletedList', 'numberedList', 'todoList', '|',
                'insertTable', 'specialCharacters', '|',
                'undo', 'redo', '|',
                '|'
            ],
            shouldNotGroupWhenFull: true
        },
        image: {
            // Configure the available styles.
            styles: [
                'alignLeft', 'alignCenter', 'alignRight'
            ],

            // Configure the available image resize options.
            resizeOptions: [
                {
                    name: 'imageResize:original',
                    label: 'Original',
                    value: null
                },
                {
                    name: 'imageResize:50',
                    label: '50%',
                    value: '50'
                },
                {
                    name: 'imageResize:75',
                    label: '75%',
                    value: '75'
                },
                {
                    name: 'imageResize:100',
                    label: '100%',
                    value: '100'
                }
            ],

            // You need to configure the image toolbar, too, so it shows the new style
            // buttons as well as the resize buttons.
            toolbar: [
                //'imageStyle:full',
                //'imageStyle:side', 
                '|',
                'imageStyle:alignLeft', 'imageStyle:alignCenter', 'imageStyle:alignRight',
                '|',
                'imageResize',
                '|',
                'imageTextAlternative'
            ]
        },

        ckfinder: {
            uploadUrl: '/ingoallla/core/connector/php/connector.php?command=QuickUpload&type=Files&responseType=json',
            
            // Open the file manager in the pop-up window.
            //openerMethod: 'popup',
            
            // https://ckeditor.com/docs/ckfinder/ckfinder3/#!/api/CKFinder.Config
            options: {
                
                resourceType: 'Images',
                readOnly : true,
                //removeModules : ['UploadFileButton', 'RenameFile', 'Html5Upload', 'FormUpload', 'DeleteFile', 'DeleteFolder'],
            },

        },
        table: {
          contentToolbar: [ 'tableColumn', 'tableRow', 'mergeTableCells' ]
        },
        indentBlock: {
            offset: 15,
            unit: "pk"
        },
        language: 'en',
    };


    if (content_type == 'html') {
        ClassicEditor.defaultConfig.removePlugins = ['Markdown', ]
    }
    
    if (content_type == 'markdown') {
    }
    
    // and finally create editor 
    ClassicEditor
        .create( document.querySelector( '#id_content' ) )
        .then( editor => {
            window.editor = editor;
            
            // configuration overload
            editor.ui.view.editable.element.style.minHeight = "280px";
            //console.log( editor );
            //console.log( Array.from( editor.ui.componentFactory.names() ) );
        } )
        .catch( error => {
            console.error( 'There was a problem initializing the editor.', error );
        } );

}

window.addEventListener("load", function(){
    CKFinder.basePath = '/api/medias/ckfinder';
    CKFinder._connectors.php = '/api/medias/ckfinder/connector/'
});
