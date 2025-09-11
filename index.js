// Public entry keeps backward compatibility; expose version only.
try {
  module.exports = { version: require('./package.json').version };
} catch (_) {
  module.exports = {};
}

