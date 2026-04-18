const fs = require('fs');
const vm = require('vm');

const code = fs.readFileSync('js/format.js', 'utf8') + '\nglobalThis.Format = Format;';
const context = {
  console,
  prompt: () => '',
  Event: class {},
};
vm.createContext(context);
vm.runInContext(code, context);

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const rendered = context.Format.render('This is **bold**, *italic*, [[UPJ Obstruction|UPJ]], and ![fig](data/images/obsidian/fig.png).');
assert(rendered.includes('<strong>bold</strong>'), 'bold should render');
assert(rendered.includes('<em>italic</em>'), 'italic should render');
assert(rendered.includes('href="#/concept/upj-obstruction"'), 'concept link should normalize id');
assert(rendered.includes('<img class="inline-image" src="data/images/obsidian/fig.png" alt="fig" loading="lazy" />'), 'local image should render');
assert(!context.Format.render('<script>alert(1)</script>').includes('<script>'), 'raw HTML should be escaped');
assert(!context.Format.render('![x](javascript:alert(1))').includes('<img'), 'unsafe image src should not render');
assert(context.Format.toPlainText('A ![x](data/images/obsidian/x.png) **bold** [[Concept|label]]') === 'A bold label', 'plain preview should remove image markup and formatting');

console.log('format renderer tests passed');
