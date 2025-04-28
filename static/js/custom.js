/**
 * ExamPrep - Основные скрипты для платформы тестирования
 */

// Дожидаемся полной загрузки DOM
document.addEventListener('DOMContentLoaded', function() {

    // Инициализация всплывающих подсказок Bootstrap
    var tooltips = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltips.map(function (tooltipEl) {
        return new bootstrap.Tooltip(tooltipEl);
    });

    // Инициализация всплывающих окон Bootstrap
    var popovers = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popovers.map(function (popoverEl) {
        return new bootstrap.Popover(popoverEl);
    });

    // Плавная прокрутка для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                const target = document.querySelector(targetId);
                if (target) {
                    window.scrollTo({
                        top: target.offsetTop - 80,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Обработчик форм квиза с AJAX
    const quizForms = document.querySelectorAll('.quiz-form');
    if (quizForms.length > 0) {
        quizForms.forEach(form => {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const submitButton = form.querySelector('button[type="submit"]');
                
                // Блокируем кнопку во время запроса
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Проверка...';
                }
                
                try {
                    const response = await fetch(form.action, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        }
                    });
                    
                    if (!response.ok) {
                        throw new Error('Ошибка сети');
                    }
                    
                    const data = await response.json();
                    
                    // Обрабатываем полученные данные
                    handleQuizResponse(data, form);
                    
                } catch (error) {
                    console.error('Произошла ошибка:', error);
                    showNotification('Произошла ошибка при отправке ответа. Попробуйте еще раз.', 'danger');
                    
                    // Восстанавливаем кнопку
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.innerHTML = 'Ответить';
                    }
                }
            });
        });
    }

    // Обработчик результата ответа на вопрос
    function handleQuizResponse(data, form) {
        // Блокируем изменение выбора ответа
        const radioInputs = form.querySelectorAll('input[type="radio"]');
        radioInputs.forEach(input => {
            input.disabled = true;
        });
        
        // Получаем контейнер для отображения результата
        const resultContainer = document.querySelector('#quiz-result');
        if (resultContainer) {
            // Отображаем результат
            resultContainer.innerHTML = `
                <div class="alert alert-${data.is_correct ? 'success' : 'danger'} fade show">
                    <div class="d-flex align-items-center">
                        <div class="fs-3 me-3">
                            <i class="fas fa-${data.is_correct ? 'check-circle' : 'times-circle'}"></i>
                        </div>
                        <div>
                            <h5>${data.is_correct ? 'Правильно!' : 'Неправильно!'}</h5>
                            ${data.explanation ? `<p>${data.explanation}</p>` : ''}
                        </div>
                    </div>
                </div>
            `;
            
            // Подсвечиваем правильный и неправильный ответы
            radioInputs.forEach(input => {
                const optionNumber = parseInt(input.value);
                const label = input.closest('label');
                
                if (optionNumber === data.correct_option) {
                    // Правильный ответ
                    label.classList.add('correct-answer');
                } else if (input.checked && optionNumber !== data.correct_option) {
                    // Неправильный выбранный ответ
                    label.classList.add('incorrect-answer');
                }
            });
            
            // Показываем кнопку "Следующий вопрос"
            const nextButton = document.querySelector('#next-question');
            if (nextButton && data.next_url) {
                nextButton.href = data.next_url;
                nextButton.style.display = 'inline-flex';
            }
        }
    }

    // Отображение уведомлений
    function showNotification(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        const notificationContainer = document.querySelector('#notifications');
        if (notificationContainer) {
            notificationContainer.innerHTML = alertHtml;
        } else {
            // Создаем контейнер, если его нет
            const container = document.createElement('div');
            container.id = 'notifications';
            container.className = 'container mt-3';
            container.innerHTML = alertHtml;
            
            const mainContent = document.querySelector('.main-content');
            if (mainContent) {
                mainContent.prepend(container);
            }
        }
    }
    
    // Анимация появления элементов при прокрутке
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    if (animatedElements.length > 0) {
        const animateOnScroll = () => {
            animatedElements.forEach(element => {
                const elementTop = element.getBoundingClientRect().top;
                const windowHeight = window.innerHeight;
                
                if (elementTop < windowHeight - 50) {
                    element.classList.add('animated');
                }
            });
        };
        
        // Запускаем при загрузке и при прокрутке
        animateOnScroll();
        window.addEventListener('scroll', animateOnScroll);
    }
});

// Функция для обновления счетчиков времени
function updateCountdown(endTime, elementId, completedCallback = null) {
    const countdownElement = document.getElementById(elementId);
    if (!countdownElement) return;
    
    const interval = setInterval(function() {
        const now = new Date().getTime();
        const distance = endTime - now;
        
        if (distance < 0) {
            clearInterval(interval);
            countdownElement.innerHTML = "Время истекло!";
            if (typeof completedCallback === 'function') {
                completedCallback();
            }
            return;
        }
        
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        
        // Форматируем вывод с ведущими нулями
        const formattedMinutes = String(minutes).padStart(2, '0');
        const formattedSeconds = String(seconds).padStart(2, '0');
        
        countdownElement.innerHTML = `${formattedMinutes}:${formattedSeconds}`;
    }, 1000);
}