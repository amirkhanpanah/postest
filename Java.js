// hook کردن متد کارت
Java.perform(function () {
    // پیدا کردن کلاس مربوط به کارت
    var CardManager = Java.use("com.tosan.behpardakht.card.CardManager"); // نام کلاس فرضی

    console.log("Hooking CardManager.onCardInserted...");

    // override متد onCardInserted
    CardManager.onCardInserted.implementation = function(track2) {
        console.log("Original onCardInserted called with: " + track2);
        // می‌توانی رفتار دلخواه اضافه کنی یا کارت شبیه‌سازی شده را بفرستی
        return this.onCardInserted.call(this, "6104336990156531=28101002252543394070");
    };

    // یا اینکه خودت متد را مستقیماً صدا بزنی:
    var manager = CardManager.$new();
    manager.onCardInserted("6104336990156531=28101002252543394070");
    console.log("Simulated card swipe!");
});
