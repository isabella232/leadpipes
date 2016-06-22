// Webfont configuration
var urls = [
    'http://s.npr.org/templates/css/fonts/GothamSSm.css',
    'http://s.npr.org/templates/css/fonts/Gotham.css',
    'http://s.npr.org/templates/css/fonts/Knockout.css'
];

if (window.location.protocol == "https:") {
    urls = [
        'https://secure.npr.org/templates/css/fonts/GothamSSm.css',
        'https://secure.npr.org/templates/css/fonts/Gotham.css',
        'https://secure.npr.org/templates/css/fonts/Knockout.css'
    ];
}

WebFont.load({
     custom: {
         families: [
             'Gotham SSm:n4,n7',
             'Gotham:n4,n7',
             'Knockout 31 4r:n4'
         ],
         urls: urls
     },
     timeout: 10000
});
