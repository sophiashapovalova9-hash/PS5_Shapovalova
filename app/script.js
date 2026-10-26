const fallbackServices = [
    { name: "Пирсинг мочки уха", price: 1500 },
    { name: "Пирсинг хряща", price: 2500 },
    { name: "Пирсинг носа", price: 2000 },
    { name: "Пирсинг пупка", price: 1500 },
    { name: "Пирсинг Монро", price: 3000 },
    { name: "Пирсинг Лабрет", price: 2000 },
    { name: "Пирсинг укус змеи", price: 2600 },
    { name: "Пирсинг укус паука", price: 4000 },
    { name: "Пирсинг георгины", price: 5000 }
];

const fallbackMasters = [
    { name: "Анна", rating: 4.9 },
    { name: "Игорь", rating: 4.7 },
    { name: "Мария", rating: 5.0 }
];

async function loadSelects() {
    const serviceSelect = document.getElementById('service');
    const masterSelect = document.getElementById('master');

    let services = fallbackServices;
    let masters = fallbackMasters;

    try {
        const servResp = await fetch('/data/api_services.json');
        if (servResp.ok) {
            const servData = await servResp.json();
            if (servData && servData.services) services = servData.services;
        }
    } catch (e) { console.log('JSON услуг не найден, берем резервные'); }

    try {
        const mastResp = await fetch('/data/api_masters.json');
        if (mastResp.ok) {
            const mastData = await mastResp.json();
            if (mastData && mastData.masters) masters = mastData.masters;
        }
    } catch (e) { console.log('JSON мастеров не найден, берем резервные'); }

    serviceSelect.innerHTML = '<option value=""> Выберите услугу </option>';
    services.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.name;
        opt.textContent = `${s.name} (${s.price} ₽)`;
        serviceSelect.appendChild(opt);
    });

    masterSelect.innerHTML = '<option value=""> Выберите мастера </option>';
    masters.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.name;
        opt.textContent = `${m.name} — рейтинг ${m.rating}`;
        masterSelect.appendChild(opt);
    });
}

async function loadData() {
    try {
        const resp = await fetch('/api/data');
        const data = await resp.json();
        const ul = document.getElementById('list');
        ul.innerHTML = '';
        
        if (data.length === 0) {
            ul.innerHTML = '<li>Заявок пока нет</li>';
            return;
        }

        data.reverse().forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<b>${item.client}</b> — ${item.service} <br><small>Мастер: ${item.master}</small>`;
            ul.appendChild(li);
        });
    } catch (e) {
        console.log('Ошибка истории:', e);
    }
}

document.getElementById('send').addEventListener('click', async () => {
    const name = document.getElementById('name').value;
    const phone = document.getElementById('phone').value;
    const service = document.getElementById('service').value;
    const master = document.getElementById('master').value;
    const msg = document.getElementById('msg');

    if (name.trim().length < 2) { msg.textContent = 'Введите имя'; return; }
    if (phone.trim().length < 5) { msg.textContent = 'Введите телефон'; return; }
    if (!service) { msg.textContent = 'Выберите услугу'; return; }
    if (!master) { msg.textContent = 'Выберите мастера'; return; }

    msg.textContent = 'Отправка...';
    msg.style.color = 'gray';

    try {
        const resp = await fetch('/api/book', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, phone, service, master })
        });
        
        const result = await resp.json();

        if (result.ok) {
            msg.style.color = 'green';
            msg.textContent = 'Заявка сохранена!';
            document.getElementById('name').value = '';
            document.getElementById('phone').value = '';
            loadData();
        } else {
            msg.style.color = 'red';
            msg.textContent = result.error;
        }
    } catch (e) {
        msg.style.color = 'red';
        msg.textContent = 'Ошибка сервера!';
    }
});

loadSelects();
loadData();