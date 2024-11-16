htmlx
=====

transform htmlx (html-like template part of jsx) to react dom dsl

I split these code from [htmlxify](https://github.com/undoZen/htmlxify) to try to make htmlx requiring work with webpack and [react-hot-loader](https://github.com/gaearon/react-hot-loaderhttps://github.com/gaearon/react-hot-loader) module, if you want to use them with browserify, just use htmlxify.

##Installation

    npm install htmlx

##Usage

    var htmlx = require('htmlx');
    var source = 'return "htmlx below",\n<p>Hello, World!</p>';
    var compiled = htmlx(source, 'fake.htmlx');

##Lisence
MIT
