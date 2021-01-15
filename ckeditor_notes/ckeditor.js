/**
 * @license Copyright (c) 2003-2020, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or https://ckeditor.com/legal/ckeditor-oss-license
 */

// The editor creator to use.
import ClassicEditorBase from '@ckeditor/ckeditor5-editor-classic/src/classiceditor';

import Essentials from '@ckeditor/ckeditor5-essentials/src/essentials';
//import UploadAdapter from '@ckeditor/ckeditor5-adapter-ckfinder/src/uploadadapter';
import Autoformat from '@ckeditor/ckeditor5-autoformat/src/autoformat';
import Bold from '@ckeditor/ckeditor5-basic-styles/src/bold';
import Italic from '@ckeditor/ckeditor5-basic-styles/src/italic';
import BlockQuote from '@ckeditor/ckeditor5-block-quote/src/blockquote';
import CKFinder from '@ckeditor/ckeditor5-ckfinder/src/ckfinder';
//import EasyImage from '@ckeditor/ckeditor5-easy-image/src/easyimage';
import Heading from '@ckeditor/ckeditor5-heading/src/heading';
import Image from '@ckeditor/ckeditor5-image/src/image';
import ImageCaption from '@ckeditor/ckeditor5-image/src/imagecaption';
import ImageStyle from '@ckeditor/ckeditor5-image/src/imagestyle';
import ImageToolbar from '@ckeditor/ckeditor5-image/src/imagetoolbar';
//import ImageUpload from '@ckeditor/ckeditor5-image/src/imageupload';

import Indent from '@ckeditor/ckeditor5-indent/src/indent';
import Link from '@ckeditor/ckeditor5-link/src/link';
import List from '@ckeditor/ckeditor5-list/src/list';
import ListStyle from '@ckeditor/ckeditor5-list/src/liststyle';

//import MediaEmbed from '@ckeditor/ckeditor5-media-embed/src/mediaembed';
import Paragraph from '@ckeditor/ckeditor5-paragraph/src/paragraph';
//import PasteFromOffice from '@ckeditor/ckeditor5-paste-from-office/src/pastefromoffice';
import Table from '@ckeditor/ckeditor5-table/src/table';
import TableToolbar from '@ckeditor/ckeditor5-table/src/tabletoolbar';
import TextTransformation from '@ckeditor/ckeditor5-typing/src/texttransformation';

import Underline from '@ckeditor/ckeditor5-basic-styles/src/underline';
import StrikeThrough from '@ckeditor/ckeditor5-basic-styles/src/strikethrough';

import todoList from '@ckeditor/ckeditor5-list/src/todolist';

import GFMDataProcessor from '@ckeditor/ckeditor5-markdown-gfm/src/gfmdataprocessor';
import Markdown from '@ckeditor/ckeditor5-markdown-gfm/src/markdown';
import Alignment from '@ckeditor/ckeditor5-alignment/src/alignment';
import HorizontalLine from '@ckeditor/ckeditor5-horizontal-line/src/horizontalline';

import CodeBlock from '@ckeditor/ckeditor5-code-block/src/codeblock';
import Code from '@ckeditor/ckeditor5-code-block/src/codeblock';

import SpecialCharacters from '@ckeditor/ckeditor5-special-characters/src/specialcharacters';

import SpecialCharactersMathematical from '@ckeditor/ckeditor5-special-characters/src/specialcharactersmathematical';
import SpecialCharactersArrows from '@ckeditor/ckeditor5-special-characters/src/specialcharactersarrows';
import SpecialCharactersLatin from '@ckeditor/ckeditor5-special-characters/src/specialcharacterslatin';
import SpecialCharactersCurrency from '@ckeditor/ckeditor5-special-characters/src/specialcharacterscurrency';

import ImageInsert from '@ckeditor/ckeditor5-image/src/imageinsert';
import ImageResize from '@ckeditor/ckeditor5-image/src/imageresize';
import AutoImage from '@ckeditor/ckeditor5-image/src/autoimage';

import WordCount from '@ckeditor/ckeditor5-word-count/src/wordcount';
import RemoveFormat from '@ckeditor/ckeditor5-remove-format/src/removeformat';

import FileRepository from '@ckeditor/ckeditor5-upload/src/filerepository';

// TODO
// import View from '@ckeditor/ckeditor5-ui/src/view';

export default class ClassicEditor extends ClassicEditorBase {}

// Plugins to include in the build.
ClassicEditor.builtinPlugins = [
	Essentials,
	//UploadAdapter,
	Autoformat,
	Bold,
	Italic,
	BlockQuote,
	CKFinder,
	//EasyImage,
	Heading,
	Image,
	ImageCaption,
	ImageStyle,
	ImageToolbar,
	//ImageUpload,
	Indent,
	Link,
	List,
    ListStyle,
	//MediaEmbed,
	Paragraph,
	//PasteFromOffice,
	Table,
	TableToolbar,
	TextTransformation,

    Underline,
    todoList,
    Markdown,
    GFMDataProcessor,
    Alignment,
    HorizontalLine,
    CodeBlock,
    Code,
    StrikeThrough,
    SpecialCharacters,
    SpecialCharactersMathematical,
    SpecialCharactersArrows,
    SpecialCharactersLatin,
    SpecialCharactersCurrency,
    
    ImageResize,
    ImageInsert,
    AutoImage,
    FileRepository,
    
    WordCount,
    RemoveFormat,
    

    // TODO
    // View,

];

// Editor configuration.
ClassicEditor.defaultConfig = {
    toolbar: {
        
        items: [
            'heading', '|',
            //'alignment', '|',
            'bold', 'italic', 'strikethrough', 'underline', 'removeformat', '|',
            'blockQuote', 'codeBlock', '|',
            'outdent', 'indent', '|',
            'imageInsert', 'link', 'horizontalLine', '|',
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
            'imageStyle:full',
            'imageStyle:side', 
            '|',
            'imageStyle:alignLeft', 'imageStyle:alignCenter', 'imageStyle:alignRight',
            '|',
            'imageResize',
            '|',
            'imageTextAlternative'
        ]
    },
    indentBlock: {
        offset: 15,
        unit: "pk"
    },
    language: 'en',
};
