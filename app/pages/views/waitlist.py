from django.conf import settings
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from datetime import datetime
import json, os


class WaitingListView(View):
    template_name = "waiting-list.html"

    def get(self, request: HttpRequest):
        launch_date = settings.LAUNCH_DATE
        return render(request, self.template_name, {"launch_date": launch_date})

    def post(self, request: HttpRequest):
        if not request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "message": "Bad request."}, status=400)

        email = request.POST.get('email', '').strip().lower()
        role = request.POST.get('role', '').strip().lower()
        valid_roles = ['client', 'provider', 'both']

        if not email or role not in valid_roles:
            return JsonResponse({
                "status": "error", 
                "message": "Please provide a valid business email and select your role."
            }, status=400)
            
        if "@" not in email:
            return JsonResponse({"status": "error", "message": "A valid email is required."}, status=400)
        
        if any(email.endswith(ext) for ext in INVALID_EMAIL_EXTS):
            return JsonResponse({
                "status": "error", 
                "message": "A valid email address is required."
            }, status=400)

        storage = WaitlistStorage()
        success, reason = storage.add_entry(email, role)
        
        if reason == "already_exists":
            return JsonResponse({
                "status": "success", 
                "message": "Access reserved! We'll be in touch."
            })

        if success:
            return JsonResponse({
                "status": "success", 
                "message": "Access Secured. Welcome to Servio."
            })
        
        return JsonResponse({"status": "error", "message": "Our engine hit a snag. Please try again later."}, status=500)

    
class WaitlistStorage:
    """Handles persistent storage for the waitlist using a JSON file."""
    
    def __init__(self):
        self.file_path = os.path.join(settings.BASE_DIR, 'private_data', 'waitlist.json')
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)

    def get_all(self):
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def add_entry(self, email, role):
        data = self.get_all()
        if any(entry['email'] == email for entry in data):
            return False, "already_exists"

        data.append({
            "email": email,
            "role": role,
            "timestamp": datetime.now().isoformat()
        })

        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        return True, "added"
    
INVALID_EMAIL_EXTS = {
    "@example.com", "@example.org", "@example.net", "@example.io",
    "@test.com", "@test.org", "@test.net", "@test.io",
    "@invalid.com", "@invalid.org",
    "@fake.com", "@fake.org", "@fake.net",
    "@demo.com", "@demo.org", "@demo.net",
    "@sample.com", "@sample.org",
    "@placeholder.com",
    "@noemail.com", "@noreply.com", "@no-reply.com",
    "@null.com", "@void.com", "@none.com",
    "@foobar.com", "@foo.com", "@bar.com", "@baz.com",
    "@qwerty.com", "@asdf.com", "@lorem.com",
    "@aaa.com", "@aaaa.com", "@abc.com", "@abcd.com",
    "@email.com", "@myemail.com",
    "@domain.com", "@yourdomain.com", "@mydomain.com",
    "@website.com", "@company.com",
    "@user.com", "@username.com",
    "@notreal.com", "@doesnotexist.com",
    "@nothing.com", "@nobody.com",

    # ── Disposable / temp mail (major providers) ──
    "@mailinator.com", "@mailinator.net", "@mailinator.org",
    "@guerrillamail.com", "@guerrillamail.net", "@guerrillamail.org",
    "@guerrillamail.biz", "@guerrillamail.de", "@guerrillamail.info", "@grr.la", 
    "@guerrillamailblock.com", "@sharklasers.com", "@guerrillamailblock.com",
    "@spam4.me", "@spamgourmet.com", "@spamgourmet.net",
    "@trashmail.com", "@trashmail.net", "@trashmail.me",
    "@trashmail.at", "@trashmail.io", "@trashmail.org",
    "@tempmail.com", "@tempmail.net", "@tempmail.org",
    "@temp-mail.org", "@temp-mail.ru", "@temp-mail.io",
    "@tempr.email", "@tempinbox.com", "@tmpmail.net",
    "@throwam.com", "@throwam.org", "@throwaway.email",
    "@dispostable.com", "@disposableemailaddresses.com", "@discard.email",
    "@yopmail.com", "@yopmail.fr", "@yopmail.net",
    "@cool.fr.nf", "@jetable.fr.nf", "@nospam.ze.tc",
    "@nomail.xl.cx", "@mega.zik.dj", "@speed.1s.fr",
    "@courriel.fr.nf", "@moncourrier.fr.nf", "@10minemail.com",
    "@maildrop.cc", "@mailnull.com", "@mailbucket.org",
    "@mailnesia.com", "@mailnesia.org",
    "@mailnull.com", "@mailscrap.com",
    "@mailexpire.com", "@mailblocks.com",
    "@10minutemail.com", "@10minutemail.net", "@10minutemail.org",
    "@10minutemail.de", "@10minutemail.co.uk",
    "@20minutemail.com", "@20minutemail.it",
    "@sharklasers.com", "@guerrillamailblock.com",
    "@fakeinbox.com", "@fakeinbox.net",
    "@filzmail.de",
    "@getnada.com",
    "@getonemail.com", "@getonemail.net",
    "@incognitomail.com", "@incognitomail.net", "@incognitomail.org",
    "@inoutmail.com", "@inoutmail.eu",
    "@jetable.com", "@jetable.net", "@jetable.org", "@jetable.fr",
    "@discard.email",
    "@mintemail.com",
    "@mohmal.com",
    "@nwldx.com",
    "@objectmail.com",
    "@obobbo.com",
    "@oneoffemail.com",
    "@pookmail.com",
    "@privy-mail.com",
    "@randomail.net",
    "@rppkn.com",
    "@safetymail.info",
    "@sendspamhere.com",
    "@shieldedmail.com",
    "@skeefmail.com",
    "@slopsbox.com",
    "@smellfear.com",
    "@sneakemail.com",
    "@sofimail.com",
    "@sogetthis.com",
    "@spamavert.com",
    "@spambob.com", "@spambob.net", "@spambob.org",
    "@spambox.us", "@spambox.info",
    "@spamcannon.com", "@spamcannon.net",
    "@spamcero.com",
    "@spamcon.org",
    "@spamcorptastic.com",
    "@spamcowboy.com", "@spamcowboy.net", "@spamcowboy.org",
    "@spamday.com",
    "@spamex.com",
    "@spamfree24.org",
    "@spamgoes.in",
    "@spamhereplease.com",
    "@spamhole.com",
    "@spamify.com",
    "@spamkill.info",
    "@spaml.com", "@spaml.de",
    "@spammotel.com",
    "@spamoff.de",
    "@spamsalad.in",
    "@spamslicer.com",
    "@spamspot.com",
    "@spamthis.co.uk",
    "@spamthisplease.com",
    "@spamtrail.com",
    "@speed.1s.fr",
    "@superrito.com",
    "@suremail.info",
    "@teleworm.com", "@teleworm.us",
    "@temporaryemail.net", "@temporaryemail.us",
    "@temporaryinbox.com",
    "@throwam.com",
    "@throwam.org",
    "@tinoza.org",
    "@trbvm.com",
    "@tryalert.com",
    "@turual.com",
    "@uggsrock.com",
    "@uroid.com",
    "@veryrealemail.com",
    "@viditag.com",
    "@viralplays.com",
    "@vomoto.com",
    "@wilemail.com",
    "@willhackforfood.biz",
    "@wuzup.net",
    "@wuzupmail.net",
    "@xagloo.com",
    "@xemaps.com",
    "@xents.com",
    "@xmaily.com",
    "@xoxy.net",
    "@xyzfree.net",
    "@yapped.net",
    "@yeah.net",
    "@yep.it",
    "@yogamaven.com",
    "@yomail.info",
    "@ypmail.webarnak.fr.eu.org",
    "@yuurok.com",
    "@zehnminuten.de",
    "@zippymail.info",
    "@zoaxe.com",
    "@zoemail.com", "@zoemail.net", "@zoemail.org",
    "@zombiesplit.com",
    "@zomg.info",
    "@zxcv.com", "@zzi.us",

    # ── Spam trap / known blacklisted domains ──
    "@spamtrap.ro",
    "@spam.la",
    "@spam.org.tr",
    "@spam.care",
    "@spam.su",
    "@antispam24.de",
    "@bumpymail.com",
    "@kasmail.com",
    "@killmail.com", "@killmail.net", "@killmail.com",
    "@kurzepost.de",
    "@lifebyfood.com",
    "@lol.ovpn.to",
    "@lolfreak.net",
    "@lookugly.com",
    "@lortemail.dk",
    "@losses.net",

    # ── Role / generic / bot-suggestive addresses (domain level) ──
    "@devnull.com",
    "@blackhole.com",
    "@bit-degree.com",
    "@binkmail.com",
    "@bobmail.info",
    "@bodhi.lawlita.com",
    "@bofthew.com",
    "@bootybay.de",
    "@boun.cr",
    "@boxformail.in",
    "@breakthru.com",
    "@brefmail.com",
    "@broadbandninja.com",
    "@buffemail.com",
    "@bugmenot.com",
    "@bumpymail.com",
    "@bund.us",

    # ── Known bot-heavy / abuse-prone free providers ──
    "@mail.ru",
    "@inbox.ru",
    "@list.ru",
    "@bk.ru",
    "@ro.ru",
    "@pochta.ru",
    "@mymail.ru",
    "@mail333.com",
    "@mailforspam.com",
    "@mailfreeonline.com",
    "@mailfree.in",
    "@mailfs.com",
    "@mailguard.me",
    "@mailimate.com",
    "@mailismagic.com",
    "@mailme.ir",
    "@mailme.lv",
    "@mailme24.com",
    "@mailmetrash.com",
    "@mailmoat.com",
    "@mailna.co", "@mailna.me",
    "@mailnew.com",
    "@mailnull.com",
    "@mailpick.biz",
    "@mailproxsy.com",
    "@mailquack.com",
    "@mailrock.biz",
    "@mailsac.com",
    "@mailscrap.com",
    "@mailshell.com",
    "@mailsiphon.com",
    "@mailslapping.com",
    "@mailslite.com",
    "@mailsoul.com",
    "@mailtome.de",
    "@mailtothis.com",
    "@mailtrash.net",
    "@mailzilla.com", "@mailzilla.org",

    # ── Misc disposable / alias services ──
    "@spamgourmet.com",
    "@trashmail.at",
    "@wegwerfmail.de", "@wegwerfmail.net", "@wegwerfmail.org",
    "@wegwerf-email.de",
    "@einrot.com",
    "@einrot.de",
    "@emailgo.de",
    "@emailisvalid.com",
    "@emaillfake.com",
    "@emailmiser.com",
    "@emailproxsy.com",
    "@emailsensei.com",
    "@emailtemporanea.com", "@emailtemporanea.net",
    "@emailtemporario.com.br",
    "@emailthe.net",
    "@emailtmp.com",
    "@emailure.net",
    "@emailwarden.com",
    "@emailx.at.hm",
    "@emailxfer.com",
    "@emailz.cf", "@emailz.ga", "@emailz.gq", "@emailz.ml", "@emailz.tk",
    "@emkei.cz", "@emkei.gq",
    "@evopo.com",
    "@explodemail.com",
    "@express.net.ua",
    "@extremail.ru",
    "@eyepaste.com",
    "@fake-box.com",
    "@fakemailgenerator.com",
    "@fakemail.fr",
    "@fastacura.com",
    "@fastchevy.com",
    "@fastchrysler.com",
    "@fastnissan.com",
    "@fastsubaru.com",
    "@fasttoyota.com",
    "@fastmazda.com",
    "@fdcserver.net",
    "@fightallspam.com",
    "@filzmail.de",
    "@fivemail.de",
    "@fixmail.tk",
    "@fizmail.com",
    "@fleckens.hu",
    "@flurred.com",
    "@flyspam.com",
    "@frapmail.com",
    "@free-email.cf", "@free-email.ga",
    "@freundin.ru",
    "@front14.org",
    "@fuckingduh.com",
    "@fudgerub.com",
    "@fux0ringduh.com",
    "@fyii.de",
    "@garbage.flu.cc", "@garbage.nixcc.com",
    "@garbagecollector.org",
    "@garbagemail.org",
    "@gardenscape.ca",
    "@gehensiemirnichtaufdensack.de",
    "@get1mail.com",
    "@get2mail.fr",
    "@getairmail.com",
    "@getmails.eu",
    "@getonemail.com",
    "@gishpuppy.com",
    "@girlsundertheinfluence.com",
    "@gishpuppy.com",
    "@gmailnew.com",
    "@gotmail.com", "@gotmail.net", "@gotmail.org",
    "@gowikibooks.com",
    "@gowikicampus.com",
    "@gowikicars.com",
    "@gowikifilms.com",
    "@gowikigames.com",
    "@gowikimusic.com",
    "@gowikinetwork.com",
    "@gowikitravel.com",
    "@gowikitv.com",
    "@great-host.in",
    "@greensloth.com",
    "@gsrv.co.uk",
    "@gustr.com",
    "@h.mintemail.com",
    "@haltospam.com",
    "@harakirimail.com",
    "@hartbot.de",
    "@hat-geld.de",
    "@hellomailo.com",
    "@herp.in",
    "@hidemail.de",
    "@hidzz.com",
    "@hmamail.com",
    "@hochsitze.com",
    "@hopemail.biz",
    "@hulapla.de",
    "@ieatspam.eu", "@ieatspam.info",
    "@ieh-mail.de",
    "@ignoremail.com",
    "@ihateyoualot.info",
    "@iheartspam.org",
    "@ilovespam.com",
    "@imails.info",
    "@inbax.tk",
    "@inbox.si",
    "@inboxclean.com",
    "@inboxdesign.me",
    "@inboxproxy.com",
    "@insorg-mail.info",
    "@instant-mail.de",
    "@ipoo.org",
    "@irish2me.com",
    "@iwi.net",

    # ── TLD-based catch-all throwaway patterns ──
    "@yopmail.pp.ua",
    "@spamgourmet.net",
    "@spamgourmet.org",
    "@mailinator.us",
}