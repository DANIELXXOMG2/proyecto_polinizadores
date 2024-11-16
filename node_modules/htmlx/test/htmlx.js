'use strict';
var htmlx = require('../');
var assert = require('assert');
describe('htmlx', function () {
  it('compiles htmlx well', function () {
    var source = 'return "htmlx below",\n<p>Hello, World!</p>';
    var compiled = htmlx(source, 'good.htmlx');
    assert(compiled.indexOf('React.DOM.p') > -1);
    assert(compiled.indexOf('good.htmlx') === -1);
  });

  it('complains about syntax error', function () {
    var source = 'return "htmlx below",\n<p>Hello, World!';
    var compiled = htmlx(source, 'error.htmlx');
    assert(compiled.indexOf('React.DOM.p') === -1);
    assert(compiled.indexOf('error.htmlx') > -1);
    assert(compiled.indexOf('failed') > -1);
  });
});
