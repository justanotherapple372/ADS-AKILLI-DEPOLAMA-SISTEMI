import simpy
import random
import matplotlib.pyplot as plt

def depoyu_calistir():
    print("--- Akıllı Depo Simülasyon Ayarları ---")
    
    try:
        robot_sayisi = int(input("Depodaki Robot Sayısı (Örn: 2): "))
        ortalama_gelis = float(input("Ürün Geliş Aralığı (Dakika, Örn: 5): "))
        min_tasima = float(input("Min Taşıma Süresi (Dakika, Örn: 2): "))
        max_tasima = float(input("max Taşıma Süresi (Dakika, Örn: 10): "))
        sim_suresi = int(input("Simülasyon Toplam Süre (Dakika, Örn: 200): "))
    except ValueError:
        print("Lütfen sayısal değerler giriniz.")
        return

    zaman_serisi = []
    bekleme_sureleri = []
    robot_kullanim_verisi = []

    class AkilliDepo:
        def __init__(self, env, n_robot):
            self.env = env
            self.robotlar = simpy.Resource(env, n_robot)
        def yerlestir(self, urun):
            sure = random.uniform(min_tasima, max_tasima)
            yield self.env.timeout(sure)

    def urun_sureci(env, isim, depo):
        varis = env.now
        with depo.robotlar.request() as talep:
            yield talep
            bekleme = env.now - varis
            bekleme_sureleri.append(bekleme)
            
            robot_kullanim_verisi.append(depo.robotlar.count)
            zaman_serisi.append(env.now)
            
            yield env.process(depo.yerlestir(isim))

    def uretici(env, depo):
        i = 0
        while True:
            yield env.timeout(random.expovariate(1.0 / ortalama_gelis))
            i += 1
            env.process(urun_sureci(env, f"Ürün-{i}", depo))

    env = simpy.Environment()
    depo = AkilliDepo(env, robot_sayisi)
    env.process(uretici(env, depo))
    env.run(until=sim_suresi)

    print("\n--- Program Tamamlandı ---")
    print(f"Toplam İşlenen Ürün: {len(bekleme_sureleri)}")
    print(f"Ortalama Bekleme Süresi: {sum(bekleme_sureleri)/len(bekleme_sureleri):.2f} dk")
    print(f"Maksimum Bekleme: {max(bekleme_sureleri):.2f} dk")

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.hist(bekleme_sureleri, bins=15, color='teal', edgecolor='black')
    plt.title(f'Bekleme Süreleri (Robot: {robot_sayisi})')
    plt.xlabel('Dakika')
    plt.subplot(1, 2, 2)
    plt.step(zaman_serisi, robot_kullanim_verisi, where='post', color='darkorange')
    plt.title('Anlık Robot Kullanımı')
    plt.ylim(0, robot_sayisi + 1)
    plt.show()

if __name__ == "__main__":
    depoyu_calistir()