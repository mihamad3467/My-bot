import { useState } from 'react';
import {
  ArrowLeft,
  ArrowUpLeft,
  AtSign,
  Bell,
  BookOpen,
  CalendarDays,
  Check,
  ChevronLeft,
  Clock3,
  Copy,
  ExternalLink,
  Heart,
  Layers3,
  Menu,
  MessageCircle,
  Moon,
  Play,
  Plus,
  Send,
  Settings2,
  ShieldCheck,
  Sparkles,
  Star,
  X,
} from 'lucide-react';

const primaryBotUrl = 'https://t.me/Quranm7bot';
const primaryHandle = '@Quranm7bot';
const secondaryTelegramUrl = 'https://t.me/dl_r7c';
const tiktokUrl = 'https://www.tiktok.com/@m.2.ia';

type Feature = {
  label: string;
  note: string;
  title: string;
  description: string;
  bullets: string[];
  icon: typeof BookOpen;
};

const features: Feature[] = [
  {
    label: 'القرآن',
    note: 'سور وآيات',
    title: 'اقرأ ما تحتاجه، في اللحظة التي تحتاجه.',
    description: 'الوصول إلى القرآن داخل تيليجرام صار بخطوة واحدة. اختر السورة، أو ابحث عن الآية، وابقَ مع النص بلا تشتت.',
    bullets: ['قائمة سور مرتبة وسريعة', 'رسائل واضحة للورد والمشاركة', 'بداية مباشرة من دون حساب جديد'],
    icon: BookOpen,
  },
  {
    label: 'الحديث',
    note: 'بالمصدر',
    title: 'معنى نبوي موثوق يرافق يومك.',
    description: 'أحاديث مختارة مع ذكر المصدر، لتقرأ وتفهم وتعود إلى المرجع حين تحتاج إلى مزيد من التثبت.',
    bullets: ['حديث اليوم في رسالة قصيرة', 'المصدر حاضر داخل المحتوى', 'اكتشاف التالي من دون بحث طويل'],
    icon: ShieldCheck,
  },
  {
    label: 'الأذكار',
    note: 'في وقتها',
    title: 'اجعل الذكر عادة، لا مهمة مؤجلة.',
    description: 'أذكار الصباح والمساء وبعد الصلاة، في أقسام واضحة وتنبيهات يمكنك ضبطها كما يناسب إيقاعك.',
    bullets: ['صباح ومساء وبعد الصلاة', 'تنبيهات اختيارية لكل قسم', 'تجربة خفيفة تحفظ تركيزك'],
    icon: Heart,
  },
  {
    label: 'الجمعة',
    note: 'كل أسبوع',
    title: 'محتوى الجمعة، حاضر قبل أن تنشغل.',
    description: 'دعاء ومحتوى الجمعة وتذكير بالأيام الفاضلة؛ حضور في وقته، بلا إشعارات عشوائية أو ازدحام.',
    bullets: ['تذكير أسبوعي بيوم الجمعة', 'محتوى ودعاء في رسالة واحدة', 'اختيار واضح للتفعيل والإيقاف'],
    icon: CalendarDays,
  },
  {
    label: 'المواقيت',
    note: 'حسب مدينتك',
    title: 'صلاتك على توقيت يومك الحقيقي.',
    description: 'أرسل مدينتك، وسيظهر لك جدول اليوم بوضوح، مع تنبيهات مستقلة تستطيع تعديلها في أي وقت.',
    bullets: ['مواقيت اليوم في نظرة واحدة', 'توقيت مرتبط بموقعك', 'تحكم كامل في تنبيهات الأذان'],
    icon: Clock3,
  },
];

const faqs = [
  {
    question: 'هل أحتاج إلى تطبيق أو حساب جديد؟',
    answer: 'لا. يكفي أن تفتح البوت داخل تيليجرام. ابدأ المحادثة مباشرة، ثم اختر ما تريد من القائمة الرئيسية.',
  },
  {
    question: 'هل أستطيع اختيار ما يصلني من التنبيهات؟',
    answer: 'نعم. يمكنك تشغيل أو إيقاف تنبيهات الأذكار والجمعة ومواقيت الصلاة بشكل مستقل من الإعدادات.',
  },
  {
    question: 'كيف تظهر مواقيت الصلاة؟',
    answer: 'بعد تحديد مدينتك، يعرض البوت مواقيت اليوم حسب منطقتك الزمنية، ويمكنك تعديل المدينة متى شئت.',
  },
  {
    question: 'من أين تأتي الأحاديث؟',
    answer: 'تظهر الأحاديث مع مصدرها داخل الرسالة نفسها؛ لتكون القراءة واضحة، والرجوع إلى المرجع ممكناً.',
  },
];

function scrollToId(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function App() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeFeature, setActiveFeature] = useState(0);
  const [openFaq, setOpenFaq] = useState(0);
  const [adhkarOn, setAdhkarOn] = useState(true);
  const [fridayOn, setFridayOn] = useState(true);
  const [query, setQuery] = useState('');
  const [querySent, setQuerySent] = useState(false);
  const [copied, setCopied] = useState(false);

  const currentFeature = features[activeFeature];
  const FeatureIcon = currentFeature.icon;

  const navigate = (id: string) => {
    setMobileMenuOpen(false);
    scrollToId(id);
  };

  const copyHandle = async () => {
    try {
      await navigator.clipboard.writeText(primaryHandle);
    } finally {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1900);
    }
  };

  const submitQuery = () => {
    if (!query.trim()) return;
    setQuerySent(true);
    window.setTimeout(() => setQuerySent(false), 2300);
  };

  return (
    <main className="quran-app" dir="rtl">
      <div className="top-strip">
        <div className="wrap top-strip-inner">
          <span className="top-strip-status"><span className="status-light" /> البوت متاح الآن على تيليجرام</span>
          <span className="top-strip-note">قرآن · حديث · أذكار · مواقيت · تذكيرات</span>
        </div>
      </div>

      <header className="header">
        <div className="wrap header-row">
          <a className="brand" href="#top" data-testid="link-brand">
            <span className="brand-emblem" aria-hidden="true"><BookOpen size={19} /></span>
            <span className="brand-copy">
              <strong>Quran</strong>
              <span>بوت القرآن على تيليجرام</span>
              <span className="handle">{primaryHandle}</span>
            </span>
          </a>
          <nav className="header-nav" aria-label="التنقل الرئيسي">
            <a href="#features" onClick={() => navigate('features')} data-testid="link-features">المزايا</a>
            <a href="#how-it-works" onClick={() => navigate('how-it-works')} data-testid="link-how-it-works">كيف يعمل</a>
            <a href="#settings" onClick={() => navigate('settings')} data-testid="link-settings">الإعدادات</a>
            <a href="#faq" onClick={() => navigate('faq')} data-testid="link-faq">الأسئلة</a>
          </nav>
          <div className="header-actions">
            <a className="button button-outline" href={secondaryTelegramUrl} target="_blank" rel="noreferrer" data-testid="link-secondary-telegram">
              @dl_r7c <ExternalLink size={14} />
            </a>
            <a className="button button-primary" href={primaryBotUrl} target="_blank" rel="noreferrer" data-testid="link-open-bot-header">
              افتح البوت <ArrowLeft size={15} />
            </a>
            <button
              className="icon-button"
              type="button"
              aria-label={mobileMenuOpen ? 'إغلاق القائمة' : 'فتح القائمة'}
              aria-expanded={mobileMenuOpen}
              onClick={() => setMobileMenuOpen((value) => !value)}
              data-testid="button-mobile-menu"
            >
              {mobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
            </button>
          </div>
        </div>
        {mobileMenuOpen && (
          <nav className="wrap mobile-nav" aria-label="تنقل الهاتف" data-testid="mobile-navigation">
            <a href="#features" onClick={() => navigate('features')} data-testid="link-mobile-features">المزايا</a>
            <a href="#how-it-works" onClick={() => navigate('how-it-works')} data-testid="link-mobile-how-it-works">كيف يعمل</a>
            <a href="#settings" onClick={() => navigate('settings')} data-testid="link-mobile-settings">الإعدادات</a>
            <a href="#faq" onClick={() => navigate('faq')} data-testid="link-mobile-faq">الأسئلة</a>
          </nav>
        )}
      </header>

      <section className="hero" id="top">
        <div className="wrap hero-grid">
          <div className="hero-copy">
            <div className="eyebrow reveal">رفيقك القرآني داخل تيليجرام</div>
            <h1 className="display hero-title reveal reveal-1">
              القرآن<br /><span className="line-accent">أقرب.</span><br /><span className="outline-word">كل يوم.</span>
            </h1>
            <p className="hero-lede reveal reveal-2">
              <strong className="proof-accent">Quran</strong> هو بوت تيليجرام الذي يضع القرآن، الحديث، الأذكار، مواقيت الصلاة وأيام الأجر في مسارك اليومي — بوضوح وسرعة.
            </p>
            <div className="hero-actions reveal reveal-3">
              <a className="button button-primary" href={primaryBotUrl} target="_blank" rel="noreferrer" data-testid="link-open-bot-hero">
                ابدأ مع {primaryHandle} <Send size={16} />
              </a>
              <button className="button button-outline" type="button" onClick={() => navigate('features')} data-testid="button-explore-features">
                استكشف المزايا <ArrowUpLeft size={16} />
              </button>
            </div>
            <div className="hero-proof reveal reveal-3">
              <span className="proof-rule" />
              <AtSign size={14} className="proof-accent" />
              <span><span className="proof-accent">{primaryHandle}</span> · بدون تطبيق إضافي</span>
            </div>
          </div>

          <div className="console-wrap" aria-label="معاينة لتجربة بوت القرآن">
            <div className="console">
              <div className="console-bar">
                <div className="console-brand"><span className="console-mark"><BookOpen size={14} /></span><span>Quran / <span className="mono">{primaryHandle}</span></span></div>
                <div className="console-actions" aria-hidden="true"><span /><span /><span /></div>
              </div>
              <div className="console-body">
                <aside className="console-side">
                  <span className="side-label">القائمة الرئيسية</span>
                  <span className="side-item active"><BookOpen size={13} /> القرآن</span>
                  <span className="side-item"><Heart size={13} /> الأذكار</span>
                  <span className="side-item"><ShieldCheck size={13} /> الحديث</span>
                  <span className="side-item"><Clock3 size={13} /> المواقيت</span>
                  <span className="side-item"><Settings2 size={13} /> الإعدادات</span>
                </aside>
                <div className="console-main">
                  <div className="console-main-head"><strong>وردك اليوم</strong><span>الأربعاء، ١٦ سبتمبر</span></div>
                  <div className="verse-card">
                    <div className="verse-top"><span>سورة الشرح · الآية ٥</span><Star size={12} /></div>
                    <blockquote>فَإِنَّ مَعَ الْعُسْرِ يُسْرًا</blockquote>
                    <cite><span>الشرح: ٥</span><span>٠٧:١٠ ص</span></cite>
                  </div>
                  <div className="console-list">
                    <div className="console-list-item"><span><b>أذكار الصباح</b><br />حان وقتها</span><Bell size={14} /></div>
                    <div className="console-list-item"><span><b>مواقيت الصلاة</b><br />اليوم · الرياض</span><Clock3 size={14} /></div>
                  </div>
                  <div className="query-box">
                    <div className="query-label"><MessageCircle size={12} /> جرّب أمراً</div>
                    <div className="query-row">
                      <input value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && submitQuery()} placeholder="اكتب: أذكار الصباح" aria-label="جرّب أمراً" data-testid="input-demo-command" />
                      <button type="button" onClick={submitQuery} aria-label="إرسال الأمر" data-testid="button-demo-command"><ChevronLeft size={15} /></button>
                    </div>
                    {querySent && <span className="query-success" data-testid="status-demo-command"><Check size={12} /> تم تجهيز طلبك للتجربة</span>}
                  </div>
                </div>
              </div>
            </div>
            <span className="float-label float-one"><Sparkles size={14} /> تجربة مركّزة</span>
            <span className="float-label float-two"><Bell size={14} /> تنبيهات باختيارك</span>
          </div>
        </div>
      </section>

      <section className="stats-band" aria-label="ملخص المزايا">
        <div className="wrap stats-grid">
          <div className="stat"><strong>٠١</strong><span>محادثة واحدة</span></div>
          <div className="stat"><strong>٠٦</strong><span>أبواب للخير</span></div>
          <div className="stat"><strong>٢٤/٧</strong><span>قريب عندما تحتاجه</span></div>
          <div className="stat"><strong>١٠٠٪</strong><span>تحكم في التنبيهات</span></div>
        </div>
      </section>

      <section className="section" id="features">
        <div className="wrap">
          <div className="section-head">
            <div>
              <div className="eyebrow">كل ما تحتاجه، من مكان واحد</div>
              <h2 className="display section-heading">أدوات هادئة.<br />حضور قوي في يومك.</h2>
            </div>
            <p className="section-lede">اختر الباب الذي تحتاجه الآن. صممنا كل قسم ليكون واضحاً وسريعاً، لا نسخة أخرى من قائمة طويلة.</p>
          </div>
          <div className="feature-shell">
            <div className="feature-stage" role="tabpanel" data-testid="feature-panel">
              <div className="stage-content">
                <span className="stage-index">FEATURE / 0{activeFeature + 1}</span>
                <h3 className="display">{currentFeature.title}</h3>
                <p>{currentFeature.description}</p>
                <ul className="stage-bullets">
                  {currentFeature.bullets.map((bullet) => <li key={bullet}><Check size={15} /> {bullet}</li>)}
                </ul>
              </div>
              <FeatureIcon className="stage-icon" strokeWidth={.65} aria-hidden="true" />
            </div>
            <div className="feature-tabs" role="tablist" aria-label="أقسام البوت">
              {features.map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <button
                    key={feature.label}
                    className={`feature-tab ${activeFeature === index ? 'active' : ''}`}
                    type="button"
                    role="tab"
                    aria-selected={activeFeature === index}
                    onClick={() => setActiveFeature(index)}
                    data-testid={`button-feature-${index}`}
                  >
                    <span className="feature-tab-icon"><Icon size={15} /></span>
                    <strong>{feature.label}</strong>
                    <small>{feature.note}</small>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      <section className="section steps-section" id="how-it-works">
        <div className="wrap">
          <div className="eyebrow">من أول ضغطة</div>
          <h2 className="display section-heading">لا إعدادات معقدة.<br />فقط ابدأ.</h2>
          <div className="steps-grid">
            <article className="step-card">
              <span className="step-no">STEP / 01</span>
              <MessageCircle className="step-icon" size={21} />
              <h3 className="display">افتح البوت</h3>
              <p>اضغط على الرابط وابدأ محادثة مباشرة مع {primaryHandle} داخل تيليجرام.</p>
            </article>
            <article className="step-card">
              <span className="step-no">STEP / 02</span>
              <Layers3 className="step-icon" size={21} />
              <h3 className="display">اختر بابك</h3>
              <p>القرآن، الحديث، الأذكار، الجمعة، المواقيت وأيام الأجر في قائمة واضحة.</p>
            </article>
            <article className="step-card">
              <span className="step-no">STEP / 03</span>
              <Settings2 className="step-icon" size={21} />
              <h3 className="display">اضبط الإيقاع</h3>
              <p>فعّل التنبيهات التي تنفعك، وأوقف ما لا تحتاجه. القرار لك طوال الوقت.</p>
            </article>
          </div>
        </div>
      </section>

      <section className="section" id="settings">
        <div className="wrap settings-grid">
          <div className="settings-copy">
            <div className="eyebrow">أنت صاحب القرار</div>
            <h2 className="display section-heading">النافع يصل.<br />والزائد يتوقف.</h2>
            <p className="section-lede">لا نرسل لك كل شيء. اختر ما تريد، واترك يومك يتنفس. لكل قسم مفتاح مستقل، وكل تغيير يظهر فوراً.</p>
            <div className="setting-note"><span className="setting-note-icon"><ShieldCheck size={15} /></span> إعدادات واضحة، وخصوصية في اختيارك</div>
          </div>
          <div className="settings-console" aria-label="معاينة إعدادات البوت">
            <div className="settings-console-head"><strong>التنبيهات</strong><span>Quran / preferences</span></div>
            <div className="setting-row">
              <div className="setting-info"><span className="setting-info-icon"><Bell size={15} /></span><span className="setting-info-copy"><strong>تنبيهات الأذكار</strong><span>{adhkarOn ? 'الصباح والمساء مفعّلان' : 'التنبيهات متوقفة'}</span></span></div>
              <button className={`toggle ${adhkarOn ? '' : 'off'}`} type="button" aria-label="تبديل تنبيهات الأذكار" aria-pressed={adhkarOn} onClick={() => setAdhkarOn((value) => !value)} data-testid="button-toggle-adhkar" />
            </div>
            <div className="setting-row">
              <div className="setting-info"><span className="setting-info-icon"><CalendarDays size={15} /></span><span className="setting-info-copy"><strong>تذكير الجمعة</strong><span>{fridayOn ? 'كل جمعة · مفعّل' : 'التذكير متوقف'}</span></span></div>
              <button className={`toggle ${fridayOn ? '' : 'off'}`} type="button" aria-label="تبديل تذكير الجمعة" aria-pressed={fridayOn} onClick={() => setFridayOn((value) => !value)} data-testid="button-toggle-friday" />
            </div>
            <div className="setting-row">
              <div className="setting-info"><span className="setting-info-icon"><Moon size={15} /></span><span className="setting-info-copy"><strong>الوضع الهادئ</strong><span>من دون تنبيهات ليلية</span></span></div>
              <span className="proof-accent"><Check size={17} /></span>
            </div>
          </div>
        </div>
      </section>

      <section className="section" id="faq">
        <div className="wrap faq-grid">
          <div>
            <div className="eyebrow">أسئلة واضحة</div>
            <h2 className="display section-heading">كل ما يلزمك<br />قبل البداية.</h2>
            <p className="section-lede">ابدأ مطمئناً. وإن لم تجد إجابتك هنا، يمكنك التواصل عبر حسابنا العام.</p>
            <a className="button button-outline" href={secondaryTelegramUrl} target="_blank" rel="noreferrer" data-testid="link-contact-secondary">
              تواصل مع @dl_r7c <ExternalLink size={14} />
            </a>
          </div>
          <div className="faq-list">
            {faqs.map((faq, index) => {
              const isOpen = openFaq === index;
              return (
                <div className="faq-item" key={faq.question}>
                  <button className={`faq-question ${isOpen ? 'open' : ''}`} type="button" aria-expanded={isOpen} onClick={() => setOpenFaq(isOpen ? -1 : index)} data-testid={`button-faq-${index}`}>
                    <span>{faq.question}</span><Plus size={18} />
                  </button>
                  {isOpen && <div className="faq-answer">{faq.answer}</div>}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="cta-section" id="start">
        <div className="wrap">
          <div className="cta-box">
            <div className="cta-content">
              <div className="eyebrow">الخطوة الأقرب</div>
              <h2 className="display">افتح القرآن.<br />وافتح يومك.</h2>
              <p>ابدأ الآن مع البوت الرسمي {primaryHandle}. محادثة واحدة تكفي لتقترب من القرآن والذكر كل يوم.</p>
              <div className="cta-actions">
                <a className="button button-primary" href={primaryBotUrl} target="_blank" rel="noreferrer" data-testid="link-open-bot-cta">
                  افتح البوت الرسمي <Send size={16} />
                </a>
                <button className="button button-outline" type="button" onClick={copyHandle} data-testid="button-copy-primary-handle">
                  {copied ? <Check size={16} /> : <Copy size={16} />} {copied ? 'تم نسخ المعرف' : `انسخ ${primaryHandle}`}
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer className="footer">
        <div className="wrap footer-row">
          <div className="footer-copy">Quran · بوت القرآن على تيليجرام · {primaryHandle}</div>
          <div className="footer-socials">
            <a className="social-link" href={secondaryTelegramUrl} target="_blank" rel="noreferrer" data-testid="link-secondary-telegram-footer"><Send size={13} /> @dl_r7c</a>
            <a className="social-link" href={tiktokUrl} target="_blank" rel="noreferrer" data-testid="link-tiktok-footer"><Play size={13} /> تيك توك</a>
          </div>
        </div>
      </footer>
    </main>
  );
}

export default App;
