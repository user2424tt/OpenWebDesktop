(function() {
    // --- 1. Переключение темы (полумесяц / солнце) ---
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');
    const body = document.body;

    // Проверим сохранённую тему в localStorage (опционально)
    const savedTheme = localStorage.getItem('webdesktop_theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark');
        themeIcon.className = 'fas fa-sun';
        themeText.textContent = 'Светлая';
    } else {
        themeIcon.className = 'fas fa-moon';
        themeText.textContent = 'Тёмная';
    }

    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark');
        const isDark = body.classList.contains('dark');
        // Меняем иконку и текст
        if (isDark) {
            themeIcon.className = 'fas fa-sun';
            themeText.textContent = 'Светлая';
        } else {
            themeIcon.className = 'fas fa-moon';
            themeText.textContent = 'Тёмная';
        }
        localStorage.setItem('webdesktop_theme', isDark ? 'dark' : 'light');
    });

    document.getElementById('auth_button').addEventListener("click", () => {
        location.href="/enter_page";
    });

    document.getElementById('file_button').addEventListener("click", () => {
        location.href="/file_page";
    });

    document.getElementById("material_button").addEventListener("click", () => {
        location.href="/material_page";
    });

    document.getElementById("items_button").addEventListener("click", () => {
        location.href="/items_page";
    });

    document.getElementById("desktop_button").addEventListener("click", () => {
        location.href="/desktop";
    });

    document.getElementById("orders_button").addEventListener("click", () => {
        location.href="/orders";
    });

    // --- 2. Стрелка вниз: плавное появление описания ---
    const arrowBtn = document.getElementById('toggleDescriptionBtn');
    const descBlock = document.getElementById('descriptionText');

    arrowBtn.addEventListener('click', () => {
        if (descBlock.classList.contains('show')) {
            // если уже показано — можно скрыть (но по задаче появляется по клику, пусть и скрывается при повторном)
            descBlock.classList.remove('show');
            // небольшой таймаут чтобы скрыть display (css-переход работает с opacity)
            setTimeout(() => {
                if (!descBlock.classList.contains('show')) {
                    descBlock.style.display = 'none';
                }
            }, 500); // после завершения transition
        } else {
            descBlock.style.display = 'block';
            // Даем браузеру момент для применения display, затем добавляем класс
            setTimeout(() => {
                descBlock.classList.add('show');
            }, 20);
        }
    });

    // если описание скрыто изначально — display none, корректно
    descBlock.style.display = 'none';

    // --- 3. Появление кнопки «Зарегистрировать компанию» при прокрутке (Intersection Observer) ---
    const registerBtn = document.getElementById('registerBtn');
    // Кнопка уже имеет анимацию popInJump, которая запускается сразу при загрузке.
    // Но по условию: "при прокрутке вниз появляется кнопка ... плавно появится и попрыгает"
    // Сейчас кнопка стартует с opacity:0 и анимация идёт при загрузке.
    // Используем Intersection Observer, чтобы запустить анимацию только когда секция попала в область видимости.
    // Сбросим её состояние и запустим по триггеру.

    // Отключаем анимацию при загрузке (убираем класс с анимацией, ставим невидимую)
    registerBtn.style.opacity = '0';
    registerBtn.style.transform = 'scale(0.5) translateY(40px)';
    registerBtn.style.animation = 'none'; // убираем автоанимацию

    // Создаём наблюдатель за триггером (можно за самой кнопкой)
    const trigger = document.getElementById('scroll-trigger');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Как только триггер (или кнопка) появился в зоне видимости - запускаем анимацию
                registerBtn.style.animation = 'popInJump 1.2s ease-out forwards';
                // После срабатывания можно отключить наблюдатель, чтобы не повторять
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 }); // 30% видимости

    // Наблюдаем за невидимым триггером или за самой кнопкой
    observer.observe(trigger);
    // на всякий случай наблюдаем и за кнопкой
    observer.observe(registerBtn);

    // Но если пользователь не проскроллит, то кнопка останется невидимой.
    // Добавим запасной вариант: если окно уже проскроллено до кнопки при загрузке, проверим вручную
    setTimeout(() => {
        const rect = registerBtn.getBoundingClientRect();
        const windowHeight = window.innerHeight;
        if (rect.top < windowHeight * 0.8) {
            // кнопка видна или почти видна - запускаем
            registerBtn.style.animation = 'popInJump 1.2s ease-out forwards';
        }
    }, 300);

    // 4. (доп) Стрелка вниз также может служить якорем, но оставим как есть.
    // Кнопки "Вход", "Рабочий стол", "Файловая система" пока неактивны — просто кнопки без ссылок.

    registerBtn.addEventListener("click", () => {
        location.href="/reg_page";
    });

})();