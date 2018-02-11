/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, {
/******/ 				configurable: false,
/******/ 				enumerable: true,
/******/ 				get: getter
/******/ 			});
/******/ 		}
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports) {

throw new Error("Module build failed: Error: The node API for `babel` has been moved to `babel-core`.\n    at Object.<anonymous> (/Users/henryhargreaves/Documents/University/Year_3/CMPS116/Project1/grepthink/node_modules/babel/index.js:1:69)\n    at Module._compile (module.js:643:30)\n    at Object.Module._extensions..js (module.js:654:10)\n    at Module.load (module.js:556:32)\n    at tryModuleLoad (module.js:499:12)\n    at Function.Module._load (module.js:491:3)\n    at Module.require (module.js:587:17)\n    at require (internal/module.js:11:18)\n    at loadLoader (/Users/henryhargreaves/Documents/University/Year_3/CMPS116/Project1/grepthink/node_modules/loader-runner/lib/loadLoader.js:13:17)\n    at iteratePitchingLoaders (/Users/henryhargreaves/Documents/University/Year_3/CMPS116/Project1/grepthink/node_modules/loader-runner/lib/LoaderRunner.js:169:2)\n    at runLoaders (/Users/henryhargreaves/Documents/University/Year_3/CMPS116/Project1/grepthink/node_modules/loader-runner/lib/LoaderRunner.js:362:2)\n    at NormalModule.doBuild (/Users/henryhargreaves/Documents/University/Year_3/CMPS116/Project1/grepthink/node_modules/webpack/lib/NormalModule.js:182:3)\n    at NormalModule.build (/Users/henryhargreaves/Documents/University/Year_3/CMPS116/Project1/grepthink/node_modules/webpack/lib/NormalModule.js:275:15)\n    at Compilation.buildModule (/Users/henryhargreaves/Documents/University/Year_3/CMPS116/Project1/grepthink/node_modules/webpack/lib/Compilation.js:151:10)\n    at moduleFactory.create (/Users/henryhargreaves/Documents/University/Year_3/CMPS116/Project1/grepthink/node_modules/webpack/lib/Compilation.js:454:10)\n    at factory (/Users/henryhargreaves/Documents/University/Year_3/CMPS116/Project1/grepthink/node_modules/webpack/lib/NormalModuleFactory.js:243:5)\n    at applyPluginsAsyncWaterfall (/Users/henryhargreaves/Documents/University/Year_3/CMPS116/Project1/grepthink/node_modules/webpack/lib/NormalModuleFactory.js:94:13)\n    at /Users/henryhargreaves/Documents/University/Year_3/CMPS116/Project1/grepthink/node_modules/tapable/lib/Tapable.js:268:11\n    at NormalModuleFactory.params.normalModuleFactory.plugin (/Users/henryhargreaves/Documents/University/Year_3/CMPS116/Project1/grepthink/node_modules/webpack/lib/CompatibilityPlugin.js:52:5)\n    at NormalModuleFactory.applyPluginsAsyncWaterfall (/Users/henryhargreaves/Documents/University/Year_3/CMPS116/Project1/grepthink/node_modules/tapable/lib/Tapable.js:272:13)\n    at resolver (/Users/henryhargreaves/Documents/University/Year_3/CMPS116/Project1/grepthink/node_modules/webpack/lib/NormalModuleFactory.js:69:10)\n    at process.nextTick (/Users/henryhargreaves/Documents/University/Year_3/CMPS116/Project1/grepthink/node_modules/webpack/lib/NormalModuleFactory.js:196:7)\n    at _combinedTickCallback (internal/process/next_tick.js:131:7)\n    at process._tickCallback (internal/process/next_tick.js:180:9)");

/***/ })
/******/ ]);