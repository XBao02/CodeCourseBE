<template>
    <div class="toast-container">
        <transition-group name="toast" tag="div">
            <div
                v-for="toast in toasts"
                :key="toast.id"
                :class="['toast', `toast-${toast.type}`]"
                @click="removeToast(toast.id)"
            >
                <div class="toast-icon">
                    <i :class="getIcon(toast.type)"></i>
                </div>
                <div class="toast-content">
                    <div class="toast-title" v-if="toast.title">{{ toast.title }}</div>
                    <div class="toast-message">{{ toast.message }}</div>
                </div>
                <button class="toast-close" @click="removeToast(toast.id)">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </transition-group>
    </div>
</template>

<script>
export default {
    name: 'ToastContainer',
    data() {
        return {
            toasts: []
        }
    },
    mounted() {
        // Listen for global toast events
        this.$root.$on('showToast', this.showToast);
    },
    beforeUnmount() {
        this.$root.$off('showToast', this.showToast);
    },
    methods: {
        showToast(options) {
            const toast = {
                id: Date.now() + Math.random(),
                type: options.type || 'info',
                title: options.title || '',
                message: options.message || '',
                duration: options.duration || 3000
            };

            this.toasts.push(toast);

            // Auto remove toast after duration
            if (toast.duration > 0) {
                setTimeout(() => {
                    this.removeToast(toast.id);
                }, toast.duration);
            }
        },

        removeToast(id) {
            const index = this.toasts.findIndex(toast => toast.id === id);
            if (index > -1) {
                this.toasts.splice(index, 1);
            }
        },

        getIcon(type) {
            const icons = {
                success: 'fas fa-check-circle',
                error: 'fas fa-exclamation-circle',
                warning: 'fas fa-exclamation-triangle',
                info: 'fas fa-info-circle'
            };
            return icons[type] || icons.info;
        }
    }
}
</script>

<style scoped>
.toast-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    pointer-events: none;
}

.toast {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    min-width: 300px;
    max-width: 400px;
    padding: 16px;
    margin-bottom: 12px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    border-left: 4px solid;
    pointer-events: auto;
    cursor: pointer;
    transition: all 0.3s ease;
}

.toast:hover {
    transform: translateX(-5px);
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2);
}

.toast-success {
    border-left-color: #27ae60;
    background: linear-gradient(135deg, #ffffff 0%, #f8fff8 100%);
}

.toast-error {
    border-left-color: #e74c3c;
    background: linear-gradient(135deg, #ffffff 0%, #fff8f8 100%);
}

.toast-warning {
    border-left-color: #f39c12;
    background: linear-gradient(135deg, #ffffff 0%, #fffdf8 100%);
}

.toast-info {
    border-left-color: #3498db;
    background: linear-gradient(135deg, #ffffff 0%, #f8fcff 100%);
}

.toast-icon {
    flex-shrink: 0;
    font-size: 20px;
    margin-top: 2px;
}

.toast-success .toast-icon {
    color: #27ae60;
}

.toast-error .toast-icon {
    color: #e74c3c;
}

.toast-warning .toast-icon {
    color: #f39c12;
}

.toast-info .toast-icon {
    color: #3498db;
}

.toast-content {
    flex: 1;
    min-width: 0;
}

.toast-title {
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 4px;
    font-size: 14px;
}

.toast-message {
    color: #555;
    font-size: 13px;
    line-height: 1.4;
    word-wrap: break-word;
}

.toast-close {
    flex-shrink: 0;
    background: none;
    border: none;
    color: #999;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: all 0.2s;
}

.toast-close:hover {
    background: rgba(0, 0, 0, 0.1);
    color: #666;
}

/* Transition animations */
.toast-enter-active {
    transition: all 0.3s ease;
}

.toast-leave-active {
    transition: all 0.3s ease;
}

.toast-enter-from {
    opacity: 0;
    transform: translateX(100%);
}

.toast-leave-to {
    opacity: 0;
    transform: translateX(100%);
}

.toast-move {
    transition: transform 0.3s ease;
}

/* Responsive */
@media (max-width: 480px) {
    .toast-container {
        top: 10px;
        right: 10px;
        left: 10px;
    }

    .toast {
        min-width: auto;
        max-width: none;
    }
}
</style>
