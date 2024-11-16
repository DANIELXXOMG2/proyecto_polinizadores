'use strict';
var reactTools = require('react-tools');
module.exports = function (content, filepath) {
    var htmlx;
    content = content.replace(/(<[^>]+)(class=)([^>]+>)/g, "$1className=$3");
    try {
      htmlx = reactTools.transform(
        '/** @jsx React.DOM */ function htmlx(state, props) { "use strict"; '+content+'};'
      , {filename: filepath});
    } catch (err) {
      htmlx = 'function htmlx(state, props) { return React.DOM.span({style: {color: "red"}}, "'+
        (filepath || 'unknown path htmlx')+' transform failed", React.DOM.br(null), "lineNumber: '+err.lineNumber+
        '", React.DOM.br(null), " column: '+err.column+
        '", React.DOM.br(null), " message: '+err.message+'");}'
    }
    return 'var React = require("react"); module.exports = function () { return htmlx.call(this, this.state, this.props); }; '+htmlx;
};
