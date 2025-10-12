// Toast plugin for Vue 3
export default {
    install(app) {
        const toast = {
            success(message, title = 'Success', duration = 3000) {
                app.config.globalProperties.$root.$emit('showToast', {
                    type: 'success',
                    title,
                    message,
                    duration
                });
            },

            error(message, title = 'Error', duration = 5000) {
                app.config.globalProperties.$root.$emit('showToast', {
                    type: 'error',
                    title,
                    message,
                    duration
                });
            },

            warning(message, title = 'Warning', duration = 4000) {
                app.config.globalProperties.$root.$emit('showToast', {
                    type: 'warning',
                    title,
                    message,
                    duration
                });
            },

            info(message, title = 'Information', duration = 3000) {
                app.config.globalProperties.$root.$emit('showToast', {
                    type: 'info',
                    title,
                    message,
                    duration
                });
            },

            show(options) {
                app.config.globalProperties.$root.$emit('showToast', options);
            }
        };

        // Add to global properties
        app.config.globalProperties.$toast = toast;
        
        // Provide for composition API
        app.provide('toast', toast);
    }
};
