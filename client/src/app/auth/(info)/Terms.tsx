import React, { useState } from "react";
import { View, TouchableOpacity, ScrollView } from "react-native";
import Markdown from "react-native-markdown-display";

// The long terms and conditions markdown text (both English and German)
const termsText = `# English Terms and Conditions (T&C):
## **Terms and Conditions (T&C)**

### **1. Bookings and Cancellations**
1.1. Bookings for courses can be **cancelled up to 3 days before the course starts**.  
1.2. Refunds for cancelled bookings are possible; however, **transaction fees (e.g., payment provider fees)** are non-refundable.  
1.3. After the 3-day deadline, no cancellations or refunds are allowed, unless the course is cancelled by the provider (e.g., gym, trainer, or organizer).  
1.4. **Course cancellations by the provider**:  
  - If the course is cancelled by the provider, users are entitled to a full refund, including transaction fees.  
  - The provider is fully responsible for covering the transaction fees and refund costs.  
1.5. Refunds may take up to **7 business days**, depending on the payment provider.  

---

### **2. Payment Methods: Stripe Connect Direct Payments vs. Transfers**

#### **2.1. Direct Payments via Stripe Connect**
- **Definition**: In Direct Payments, the user pays the full amount directly to the provider (e.g., gym, trainer, or organizer) through Stripe Connect. The platform acts solely as a technical intermediary.  
- **Usage**:
  - Used when a user books a course from a single provider.  
  - Ideal for straightforward, direct bookings without involving multiple providers.  
- **Refunds**:
  - Refunds are processed exclusively by the provider.  
  - The platform provides technical support but is not responsible for the refund process.  
  - Transaction fees (e.g., Stripe fees) are **not borne by the provider** if the refund is initiated by the user.  
- **Transaction Fees**:
  - Stripe transaction fees are deducted from the original payment and are non-refundable.  

---

#### **2.2. Transfers for Bundle Bookings via Stripe Connect**
- **Definition**: In Transfers, the user pays the total amount to the platform via Stripe Connect. The platform then distributes the payment to multiple providers.  
- **Usage**:
  - Used when a booking includes courses from multiple providers.  
  - Allows splitting payments among multiple providers.  
- **Refunds**:
  - The platform coordinates refunds on behalf of the providers.  
  - Refunds are issued proportionally based on the original booking amounts.  
  - Transaction fees (e.g., Stripe fees) are **not refunded**, unless the refund is due to a cancellation by the provider.  
  - If a provider lacks sufficient funds, the refund may be delayed or offset against future earnings.  
- **Transaction Fees**:
  - Stripe transaction fees are proportionally borne by the providers.  

---

### **3. Memberships**
3.1. Memberships have a fixed minimum term.  
3.2. Upon account deletion, the membership is automatically terminated; however, access and usage remain available until the end of the minimum term.  
3.3. Refunds for membership fees are excluded unless legally required.  

---

### **4. Account Deletion Rules**
4.1. When a user deletes their account, no automatic refunds for existing or future bookings/transactions are issued.  
4.2. Refunds must be directly resolved with the respective providers, especially for Direct Payments.  
4.3. Already booked courses can still be attended after account deletion as long as they remain active.  
4.4. Memberships automatically terminate at the end of their minimum term unless cancelled before account deletion.  

---

### **5. Use of QR Codes**
5.1. Participation in courses requires the presentation of a personalized QR code.  
5.2. The QR code contains only a pseudonymized ID and no personal data.  
5.3. The QR code must be kept confidential. In case of loss or misuse, a replacement can be requested.  
5.4. The QR code is solely for verifying bookings and cannot be transferred to third parties.  

---

### **6. Liability**
6.1. The platform is not liable for services provided directly by providers (e.g., gyms, trainers, or organizers).  
6.2. For individual refunds or other claims, users must contact the respective provider directly, especially for Direct Payments.  
6.3. If a course is cancelled by the provider, the provider is responsible for the full refund of booking costs and transaction fees.  
6.4. The platform is not liable for delays in refunds caused by payment providers, providers, or technical issues.  

---

### **7. Transaction and Refund Policies**
7.1. Refunds are issued to the original payment method used by the user.  
7.2. **Refunds for Direct Payments**:
   - The provider is solely responsible for processing refunds.  
   - The platform is not liable for delays or issues in the refund process.  
   - Transaction fees are not covered by the provider for user-initiated refunds.  
7.3. **Refunds for Transfers**:
   - The platform coordinates refunds on behalf of providers.  
   - Refunds may be delayed if a provider lacks sufficient funds.  
   - The affected provider has 3 business days to provide the required funds.  
7.4. **Offsetting refunds against future earnings**:
   - If a provider lacks sufficient funds, refunds may be offset against the provider's future earnings.  

---

### **8. Changes to the T&C**
8.1. The platform reserves the right to amend these T&C at any time.  
8.2. Users and providers will be informed of any significant changes at least 14 days in advance.  

# German Terms and Conditions (AGB):
## **Allgemeine Geschäftsbedingungen (AGB)**

### **1. Buchungen und Stornierungen**
1.1. Buchungen für Kurse können **bis spätestens 3 Tage vor Kursbeginn** storniert werden.  
1.2. Rückerstattungen für stornierte Buchungen sind möglich, jedoch werden **Transaktionsgebühren (z. B. Zahlungsdienstleistergebühren)** nicht zurückerstattet.  
1.3. Nach Ablauf der 3-Tages-Frist ist keine Stornierung oder Rückerstattung mehr möglich, es sei denn, der Kurs wird durch den Anbieter (z. B. Fitnessstudio, Trainer oder Veranstalter) abgesagt.  
1.4. **Kursabsagen durch den Anbieter**:  
  - Bei einer Kursabsage durch den Anbieter erhalten Nutzer eine vollständige Rückerstattung, einschließlich der Transaktionsgebühren.  
  - Die Transaktionsgebühren und Rückerstattungskosten werden vollständig vom Anbieter getragen.  
1.5. Rückerstattungen können je nach Zahlungsanbieter **bis zu 7 Werktage** dauern.  

---

### **2. Zahlungsmethoden: Stripe Connect Direct Payments vs. Transfers**

#### **2.1. Direct Payments über Stripe Connect**
- **Definition**: Bei Direct Payments erfolgt die Zahlung des Nutzers direkt an den Anbieter (z. B. Fitnessstudio, Trainer oder Veranstalter) über Stripe Connect. Die Plattform agiert nur als technischer Vermittler.  
- **Verwendung**:
  - Wird verwendet, wenn ein Nutzer ausschließlich einen Kurs eines einzigen Anbieters bucht.  
  - Ideal für einfache, direkte Buchungen ohne Beteiligung mehrerer Anbieter.  
- **Rückerstattungen**:
  - Rückerstattungen werden ausschließlich durch den Anbieter abgewickelt.  
  - Die Plattform stellt technische Mittel bereit, übernimmt jedoch keine Verantwortung für die Abwicklung.  
  - Transaktionsgebühren (z. B. Stripe-Gebühren) werden **nicht vom Anbieter getragen**, wenn der Nutzer die Rückerstattung initiiert.  
- **Transaktionsgebühren**:
  - Die Stripe-Transaktionsgebühren werden bei der ursprünglichen Zahlung abgezogen und nicht zurückerstattet.  

---

#### **2.2. Transfers für Sammelbuchungen über Stripe Connect**
- **Definition**: Bei Sammelbuchungen zahlt der Nutzer den Gesamtbetrag zunächst an die Plattform über Stripe Connect. Die Plattform verteilt den Betrag anschließend an die jeweiligen Anbieter.  
- **Verwendung**:
  - Wird verwendet, wenn eine Buchung Kurse von mehreren Anbietern umfasst.  
  - Ermöglicht die Verteilung der Zahlung zwischen mehreren Anbietern.  
- **Rückerstattungen**:
  - Die Plattform koordiniert Rückerstattungen im Namen der Anbieter.  
  - Rückerstattungen erfolgen anteilig je nach Anteil der ursprünglichen Buchung.  
  - Transaktionsgebühren (z. B. Stripe-Gebühren) werden **nicht zurückerstattet**, es sei denn, die Rückerstattung erfolgt aufgrund einer Absage durch den Anbieter.  
  - Wenn ein Anbieter keine ausreichenden Mittel hat, kann die Rückerstattung verzögert oder mit zukünftigen Einnahmen verrechnet werden.  
- **Transaktionsgebühren**:
  - Die Stripe-Transaktionsgebühren werden anteilig von den Anbietern getragen.  

---

### **3. Memberships (Mitgliedschaften)**
3.1. Memberships haben eine festgelegte Mindestlaufzeit.  
3.2. Nach einer Kontolöschung wird die Membership automatisch beendet, jedoch bleibt der Zugang und die Nutzung bis zum Ende der Mindestlaufzeit bestehen.  
3.3. Eine Rückerstattung der Membershipsgebühren ist ausgeschlossen, es sei denn, eine gesetzliche Pflicht zur Rückerstattung besteht.  

---

### **4. Regeln bei Accountlöschung**
4.1. Wenn ein Nutzer seinen Account löscht, werden keine automatischen Rückerstattungen für bestehende oder zukünftige Buchungen/Transaktionen durchgeführt.  
4.2. Rückerstattungen müssen direkt mit den jeweiligen Anbietern geklärt werden, insbesondere bei Direct Payments.  
4.3. Bereits gebuchte Kurse können auch nach einer Accountlöschung weiterhin besucht werden, solange sie aktiv sind.  
4.4. Memberships enden automatisch nach Ablauf der Mindestlaufzeit, es sei denn, sie werden vor der Kontolöschung gekündigt.  

---

### **5. Nutzung des QR-Codes**
5.1. Die Teilnahme an Kursen erfolgt über die Vorlage eines personalisierten QR-Codes.  
5.2. Der QR-Code enthält ausschließlich eine pseudonymisierte ID und keine personenbezogenen Daten.  
5.3. Der QR-Code ist vertraulich zu behandeln. Bei Verlust oder Missbrauch kann ein Ersatz angefordert werden.  
5.4. Der QR-Code dient ausschließlich zur Verifizierung der Buchung und kann nicht an Dritte übertragen werden.  

---

### **6. Haftung**
6.1. Die Plattform haftet nicht für Leistungen, die direkt von den Anbietern (z. B. Fitnessstudios, Trainern oder Veranstaltern) erbracht werden.  
6.2. Für individuelle Rückerstattungen oder andere Ansprüche müssen sich Nutzer direkt an den jeweiligen Anbieter wenden, insbesondere bei Direct Payments.  
6.3. Bei einer Kursabsage durch den Anbieter haftet der Anbieter für die vollständige Rückerstattung der Buchungskosten und Transaktionsgebühren.  
6.4. Die Plattform haftet nicht für Verzögerungen bei Rückerstattungen, die durch Zahlungsdienstleister, Anbieter oder technische Probleme verursacht werden.  

---

### **7. Transaktions- und Rückerstattungsrichtlinien**
7.1. Rückerstattungen erfolgen auf die ursprüngliche Zahlungsmethode des Nutzers.  
7.2. **Rückerstattungen bei Direct Payments**:
   - Der Anbieter ist allein verantwortlich für die Rückerstattung.  
   - Die Plattform ist nicht haftbar für Verzögerungen oder Probleme bei der Rückerstattung.  
   - Transaktionsgebühren werden bei einer Rückerstattung durch den Nutzer nicht vom Anbieter getragen.  
7.3. **Rückerstattungen bei Transfers**:
   - Die Plattform koordiniert Rückerstattungen im Namen der Anbieter.  
   - Rückerstattungen können verzögert sein, wenn ein Anbieter nicht über ausreichende Mittel verfügt.  
   - Der betroffene Anbieter erhält eine Frist von 3 Werktagen, um die erforderlichen Mittel bereitzustellen.  
7.4. **Verrechnung mit zukünftigen Einnahmen**:
   - Wenn ein Anbieter nicht über ausreichende Mittel verfügt, können Rückerstattungen mit zukünftigen Einnahmen des Anbieters verrechnet werden.  

---

### **8. Änderungen der AGB**
8.1. Die Plattform behält sich das Recht vor, diese AGB jederzeit zu ändern.  
8.2. Nutzer und Anbieter werden über wesentliche Änderungen mindestens 14 Tage im Voraus informiert.  
`;

const Terms = () => {
  // State to track if the user has scrolled to the bottom
  const [scrolledToBottom, setScrolledToBottom] = useState(false);

  // Handler for the scroll event to check if the bottom is reached
  const handleScroll = (event: any) => {
    const { layoutMeasurement, contentOffset, contentSize } = event.nativeEvent;
    // Check if the user has scrolled to within 20 pixels of the bottom
    if (layoutMeasurement.height + contentOffset.y >= contentSize.height - 20) {
      setScrolledToBottom(true);
    }
  };

  return (
    // Main container filling the screen with content above the bottom bar
    <View className="flex-1 bg-light_primary dark:bg-dark_primary justify-between">
      
      {/* Scrollable container for the markdown content */}
      <ScrollView
        className="flex-1 px-4"
        contentContainerStyle={{ paddingVertical: 20 }}
        showsVerticalScrollIndicator={false}
        onScroll={handleScroll}
        scrollEventThrottle={16} // Throttle scroll events for performance
      >
        {/* Render the markdown text using the Markdown component */}
        <Markdown
          style={{
            body: { color: "#000", fontSize: 16 },
            heading1: { color: "#000" },
            heading2: { color: "#000" },
            // Add more styles as needed for different markdown elements
          }}
        >
          {termsText}
        </Markdown>
      </ScrollView>

      {/* Bottom bar with two buttons */}
      <View className="flex-row justify-around items-center bg-white dark:bg-gray-800 py-4 border-t border-gray-200 dark:border-gray-700">
        {/* Decline button is always active */}
        <TouchableOpacity
          onPress={() => console.log("Ablehnen pressed")}
          className="p-4 rounded-md"
        >
          <Markdown
            style={{
              body: { color: "red", fontSize: 18, fontWeight: "bold" },
            }}
          >
            Ablehnen
          </Markdown>
        </TouchableOpacity>
        
        {/* Accept button is disabled until scrolled to bottom */}
        <TouchableOpacity
          onPress={() => {
            if (scrolledToBottom) {
              console.log("Akzeptieren pressed");
            }
          }}
          disabled={!scrolledToBottom}
          className={`p-4 rounded-md ${scrolledToBottom ? "" : "bg-gray-300"}`}
        >
          <Markdown
            style={{
              body: {
                color: scrolledToBottom ? "green" : "gray",
                fontSize: 18,
                fontWeight: "bold",
              },
            }}
          >
            Akzeptieren
          </Markdown>
        </TouchableOpacity>
      </View>
      
    </View>
  );
};

export default Terms;