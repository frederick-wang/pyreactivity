## [0.0.6](https://github.com/frederick-wang/pyreactivity/compare/v0.0.5...v0.0.6) (2023-01-19)


### Bug Fixes

* 1. rename DEV to DEBUG; 2. Fixed the bug that after assigning empty value to some reactive objs ([febe793](https://github.com/frederick-wang/pyreactivity/commit/febe793f622554238e4321bb568c1eb61c0f28ca))



## [0.0.5](https://github.com/frederick-wang/pyreactivity/compare/v0.0.4...v0.0.5) (2023-01-17)


### Bug Fixes

* **reactive:** fix the bug of proxy ([6161311](https://github.com/frederick-wang/pyreactivity/commit/61613114d759f9e646038bcdd530e3bd8c635fd6))
* **reactive:** fix the support of ndarray ([6e4aba8](https://github.com/frederick-wang/pyreactivity/commit/6e4aba8f85da4e8cb9c547b9ea816b17c8bfccc4))



## [0.0.4](https://github.com/frederick-wang/pyreactivity/compare/v0.0.3...v0.0.4) (2023-01-17)


### Bug Fixes

* **patches:** fix the support of Ref for json ([e83b2c3](https://github.com/frederick-wang/pyreactivity/commit/e83b2c39d316c78ab8daa17f60f91f93388fc067))


### Features

* **patches:** add patch_json() and unpatch_json() functions ([354b2ee](https://github.com/frederick-wang/pyreactivity/commit/354b2ee4f17aa31cb1a92251196253ef2723e10b))
* **ref/reactivity:** add deep_unref() and deep_to_raw() ([c82afa6](https://github.com/frederick-wang/pyreactivity/commit/c82afa661e26fe7717fb1eab6fba50a17ba38080))



## [0.0.3](https://github.com/frederick-wang/pyreactivity/compare/637b5936d3a82bfaacdddc55419dbdd2ced82b68...v0.0.3) (2023-01-16)


### Bug Fixes

* **effect:** fix reportPrivateImportUsage. ([45094be](https://github.com/frederick-wang/pyreactivity/commit/45094becd4c4e2890cc0a5644b7937be2276ae47))
* explicitly export symbols in modules. ([c712d74](https://github.com/frederick-wang/pyreactivity/commit/c712d740a0bd98d9fa5fb19bd8cdd3682584b79d))
* **reactive:** add missing type and method ([e25b026](https://github.com/frederick-wang/pyreactivity/commit/e25b026ef9b4a4919779add401995a53274ecd13))
* **reactive:** Fix the bug __len__ isn't tracked. ([0fc98a3](https://github.com/frederick-wang/pyreactivity/commit/0fc98a3dee3e3acf75956aa9c970101b649b08e9))
* **reactive:** items() and values() of dict fixed. ([08dceb2](https://github.com/frederick-wang/pyreactivity/commit/08dceb2bcf45e764e15b892047c619471590af59))
* **reactive:** Lost reactivity after assigning. ([4f00443](https://github.com/frederick-wang/pyreactivity/commit/4f0044304db7a09cc2a6c253377b35fb3fb6fee7))
* **reactive:** reactive() return type fixed. ([6585650](https://github.com/frederick-wang/pyreactivity/commit/6585650e49f4b66300242fea05644a112b1461b1))
* **reactive:** TypeError message typo fixed. ([eeaa2e5](https://github.com/frederick-wang/pyreactivity/commit/eeaa2e52fb63bbdcedb91e2a6f891fcee7962de8))
* **ref:** overload the ref() function ([97e0d9e](https://github.com/frederick-wang/pyreactivity/commit/97e0d9ee25322e237b863662fb34d6c33961da11))
* **tests:** typo fixed. ([3695bb2](https://github.com/frederick-wang/pyreactivity/commit/3695bb2314d53dd73a4ffb3dd7706c770dbc9651))


### Features

* **patches:** add support of ref for json.dumps ([9de85d9](https://github.com/frederick-wang/pyreactivity/commit/9de85d9b5b5b6f7ca4db52ec073da05c227a7e31))
* **reactive:** new util methods added. ([637b593](https://github.com/frederick-wang/pyreactivity/commit/637b5936d3a82bfaacdddc55419dbdd2ced82b68))
* **tests:** add a new case to test_reactive. ([246a2bb](https://github.com/frederick-wang/pyreactivity/commit/246a2bbe91ad69be54e6533f82d3b58a13c6277c))



