(function () {
    'use strict';

    var configModule = angular.module('flexget.module.config', ['schemaForm']);
    registerPlugin(configModule);

    configModule.run(function (route, sideNav) {
        route.register('config', '/config', 'configController', 'plugins/config/config.tmpl.html');
        sideNav.register('/config', 'Config', 'fa fa-settings', 128);
    });

})();