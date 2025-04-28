/**
 * ExamPrep - Специальные скрипты для интерактивности тестов
 */

class Quiz {
    constructor(config) {
        this.config = {
            formSelector: '#quiz-form',
            resultSelector: '#quiz-result',
            nextButtonSelector: '#next-question',
            optionsSelector: 'input[type="radio"]',
            submitButtonSelector: '#submit-answer',
            ...config
        };
        
        this.form = document.querySelector(this.config.formSelector);
        this.resultContainer = document.querySelector(this.config.resultSelector);
        this.nextButton = document.querySelector(this.config.nextButtonSelector);
        this.options = document.querySelectorAll(this.config.optionsSelector);
        this.submitButton = document.querySelector(this.config.submitButtonSelector);
        
        this.isSubmitting = false;
        
        this.init();
    }
    
    init() {
        if (!this.form) return;
        
        // Включаем кнопку "Ответить" только если выбран вариант
        this.checkFormValidity();
        
        // Добавляем обработчики событий
        this.attachEventListeners();
    }
    
    attachEventListeners() {
        // Проверка валидности при изменении выбора
        this.options.forEach(option => {
            option.addEventListener('change', () => this.checkFormValidity());
        });
        
        // AJAX отправка формы
        this.form.addEventListener('submit', (event) => this.handleSubmit(event));
        
        // Анимации при наведении на варианты ответов
        this.addHoverAnimations();
    }
    
    checkFormValidity() {
        if (!this.submitButton) return;
        
        const isChecked = Array.from(this.options).some(input => input.checked);
        this.submitButton.disabled = !isChecked;
        
        if (isChecked) {
            this.submitButton.classList.add('pulse-animation');
        } else {
            this.submitButton.classList.remove('pulse-animation');
        }
    }
    
    async handleSubmit(event) {
        event.preventDefault();
        
        // Предотвращаем двойную отправку
        if (this.isSubmitting) return;
        this.isSubmitting = true;
        
        // Визуальная обратная связь при отправке
        if (this.submitButton) {
            this.submitButton.disabled = true;
            this.submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Проверка...';
        }
        
        try {
            // Собираем данные формы
            const formData = new FormData(this.form);
            
            // Отправляем AJAX запрос
            const response = await fetch(this.form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });
            
            if (!response.ok) {
                throw new Error('Ошибка сети при отправке ответа');
            }
            
            const data = await response.json();
            
            // Обрабатываем полученные данные
            this.handleResponse(data);
            
        } catch (error) {
            console.error('Произошла ошибка:', error);
            this.showError(error.message || 'Произошла ошибка при отправке ответа');
            
            // Восстанавливаем кнопку
            if (this.submitButton) {
                this.submitButton.disabled = false;
                this.submitButton.innerHTML = '<i class="fas fa-check me-2"></i> Ответить';
                this.isSubmitting = false;
            }
        }
    }
    
    handleResponse(data) {
        // Блокируем изменение выбора ответа
        this.options.forEach(input => {
            input.disabled = true;
        });
        
        // Скрываем кнопку ответа
        if (this.submitButton) {
            this.submitButton.style.display = 'none';
        }
        
        // Отображаем результат
        this.showResult(data);
        
        // Подсвечиваем правильный и неправильный ответы с анимацией
        this.highlightAnswers(data);
        
        // Показываем кнопку "Следующий вопрос"
        this.showNextButton(data);
    }
    
    showResult(data) {
        if (!this.resultContainer) return;
        
        const resultClass = data.is_correct ? 'success' : 'danger';
        const resultIcon = data.is_correct ? 'check-circle' : 'times-circle';
        const resultTitle = data.is_correct ? 'Правильно!' : 'Неправильно!';
        const explanationHtml = data.explanation ? `<p class="mb-0">${data.explanation}</p>` : '';
        
        this.resultContainer.innerHTML = `
            <div class="alert alert-${resultClass} mt-3 fade show">
                <div class="d-flex">
                    <div class="fs-3 me-3">
                        <i class="fas fa-${resultIcon}"></i>
                    </div>
                    <div>
                        <h5>${resultTitle}</h5>
                        ${explanationHtml}
                    </div>
                </div>
            </div>
        `;
        
        // Добавляем анимацию для привлечения внимания
        const resultAlert = this.resultContainer.querySelector('.alert');
        resultAlert.classList.add('pulse-animation');
        
        // Плавно прокручиваем к результату
        setTimeout(() => {
            this.resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 200);
    }
    
    highlightAnswers(data) {
        this.options.forEach(input => {
            const optionNumber = parseInt(input.value);
            const label = input.closest('.option-label');
            
            if (optionNumber === data.correct_option) {
                // Правильный ответ
                label.classList.add('correct-answer');
                setTimeout(() => {
                    label.classList.add('pulse-animation');
                }, 300);
            } else if (input.checked && optionNumber !== data.correct_option) {
                // Неправильный выбранный ответ
                label.classList.add('incorrect-answer');
                label.classList.add('shake-animation');
            }
        });
    }
    
    showNextButton(data) {
        if (!this.nextButton) return;
        
        if (data.next_url) {
            this.nextButton.href = data.next_url;
            this.nextButton.innerHTML = '<i class="fas fa-arrow-right me-2"></i> Следующий вопрос';
        } else {
            // Если нет следующего вопроса, показываем кнопку "Завершить"
            const topicDetailUrl = this.nextButton.getAttribute('data-topic-url');
            this.nextButton.href = topicDetailUrl;
            this.nextButton.innerHTML = '<i class="fas fa-flag-checkered me-2"></i> Завершить тест';
        }
        
        this.nextButton.style.display = 'inline-flex';
        
        // Добавляем пульсирующую анимацию для привлечения внимания
        setTimeout(() => {
            this.nextButton.classList.add('pulse-animation');
        }, 1000);
    }
    
    showError(message) {
        if (!this.resultContainer) return;
        
        this.resultContainer.innerHTML = `
            <div class="alert alert-danger mt-3">
                <div class="d-flex">
                    <div class="fs-3 me-3">
                        <i class="fas fa-exclamation-circle"></i>
                    </div>
                    <div>
                        <h5>Ошибка</h5>
                        <p class="mb-0">${message}</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    addHoverAnimations() {
        const optionLabels = document.querySelectorAll('.option-label');
        
        optionLabels.forEach(label => {
            label.addEventListener('mouseenter', function() {
                if (!this.classList.contains('correct-answer') && 
                    !this.classList.contains('incorrect-answer')) {
                    this.style.transform = 'translateY(-2px)';
                    this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
                }
            });
            
            label.addEventListener('mouseleave', function() {
                this.style.transform = '';
                this.style.boxShadow = '';
            });
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация квиза, если находимся на странице с тестом
    if (document.querySelector('#quiz-form')) {
        const quizApp = new Quiz({
            topicDetailUrl: document.querySelector('#next-question').getAttribute('data-topic-url')
        });
    }
    
    // Дополнительные CSS-анимации
    document.head.insertAdjacentHTML('beforeend', `
        <style>
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            @keyframes shake {
                0% { transform: translateX(0); }
                20% { transform: translateX(-5px); }
                40% { transform: translateX(5px); }
                60% { transform: translateX(-3px); }
                80% { transform: translateX(3px); }
                100% { transform: translateX(0); }
            }
            
            .pulse-animation {
                animation: pulse 0.5s ease-in-out;
            }
            
            .shake-animation {
                animation: shake 0.5s ease-in-out;
            }
        </style>
    `);
});