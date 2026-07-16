document.addEventListener("DOMContentLoaded", function () {
  // --- UI Elements ---
  const passengersSlider = document.getElementById("rider-height");
  const trunkSlider = document.getElementById("rider-inseam");
  const valPassengers = document.getElementById("val-height");
  const valTrunk = document.getElementById("val-inseam");

  const step1 = document.getElementById("quiz-step-1");
  const step2 = document.getElementById("quiz-step-2");
  const step3 = document.getElementById("quiz-step-3");
  const resultsWrapper = document.getElementById("results-wrapper");

  const btnNext1 = document.getElementById("btn-next-1");
  const btnNext2 = document.getElementById("btn-next-2");
  const btnBack2 = document.getElementById("btn-back-2");
  const btnBack3 = document.getElementById("btn-back-3");
  const btnSubmit = document.getElementById("btn-submit");
  const btnReset = document.getElementById("btn-reset");

  const badge1 = document.getElementById("badge-step-1");
  const badge2 = document.getElementById("badge-step-2");
  const badge3 = document.getElementById("badge-step-3");
  const stepTitle = document.getElementById("step-title");

  // --- Dynamic Slider Updates ---
  if (passengersSlider && valPassengers) {
    passengersSlider.addEventListener("input", function () {
      valPassengers.textContent = passengersSlider.value;
    });
  }

  if (trunkSlider && valTrunk) {
    trunkSlider.addEventListener("input", function () {
      valTrunk.textContent = trunkSlider.value;
    });
  }

  const budgetSlider = document.getElementById("max-budget");
  const valBudget = document.getElementById("val-budget");

  if (budgetSlider && valBudget) {
    budgetSlider.addEventListener("input", function () {
      const formatted = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        maximumFractionDigits: 0
      }).format(budgetSlider.value);
      valBudget.textContent = formatted;
    });
  }

  // --- Interactive Radio Cards ---
  const radioLabels = document.querySelectorAll(".radio-card");
  radioLabels.forEach(label => {
    label.addEventListener("click", function () {
      const radioInput = label.querySelector("input[type='radio']");
      if (radioInput) {
        const groupName = radioInput.getAttribute("name");
        const groupLabels = document.querySelectorAll(`input[name='${groupName}']`);
        groupLabels.forEach(input => {
          input.closest(".radio-card").classList.remove("selected");
        });
        radioInput.checked = true;
        label.classList.add("selected");
      }
    });
  });

  // --- Form Navigation ---
  if (btnNext1) {
    btnNext1.addEventListener("click", function () {
      step1.classList.add("hidden");
      step2.classList.remove("hidden");
      badge1.classList.remove("active");
      badge2.classList.add("active");
      stepTitle.textContent = "Passo 2: Motorização & Câmbio";
    });
  }

  if (btnBack2) {
    btnBack2.addEventListener("click", function () {
      step2.classList.add("hidden");
      step1.classList.remove("hidden");
      badge2.classList.remove("active");
      badge1.classList.add("active");
      stepTitle.textContent = "Passo 1: Suas Necessidades de Espaço";
    });
  }

  if (btnNext2) {
    btnNext2.addEventListener("click", function () {
      step2.classList.add("hidden");
      step3.classList.remove("hidden");
      badge2.classList.remove("active");
      badge3.classList.add("active");
      stepTitle.textContent = "Passo 3: Orçamento & Uso";
    });
  }

  if (btnBack3) {
    btnBack3.addEventListener("click", function () {
      step3.classList.add("hidden");
      step2.classList.remove("hidden");
      badge3.classList.remove("active");
      badge2.classList.add("active");
      stepTitle.textContent = "Passo 2: Motorização & Câmbio";
    });
  }

  if (btnSubmit) {
    btnSubmit.addEventListener("click", function () {
      calculateMatches();
    });
  }

  if (btnReset) {
    btnReset.addEventListener("click", function () {
      resultsWrapper.classList.add("hidden");
      document.querySelector(".quiz-card").classList.remove("hidden");
      step3.classList.add("hidden");
      step1.classList.remove("hidden");
      badge3.classList.remove("active");
      badge1.classList.add("active");
      stepTitle.textContent = "Passo 1: Suas Necessidades de Espaço";
    });
  }

  // --- Matching Engine Algorithm ---
  function calculateMatches() {
    const passengers = parseFloat(passengersSlider.value);
    const trunk = parseFloat(trunkSlider.value);
    const propulsion = document.querySelector("input[name='experience']:checked").value;
    const requireAutomatic = document.getElementById("require-abs").checked;
    const preferEconomical = document.getElementById("prefer-lightweight").checked;
    const roadType = document.querySelector("input[name='road-type']:checked").value;
    const location = document.querySelector("input[name='location']:checked").value;
    const maxBudget = parseFloat(document.getElementById("max-budget").value);
    const strictBudget = document.getElementById("strict-budget").checked;
    const condition = document.querySelector("input[name='bike-condition']:checked").value;

    const dataElement = document.getElementById("motorcycles-json");
    if (!dataElement) return;
    let cars = JSON.parse(dataElement.textContent);

    // Filter by conservation state
    if (condition === "new") {
      cars = cars.filter(c => c.is_used !== true);
    } else if (condition === "used") {
      cars = cars.filter(c => c.is_used === true);
    }

    let scoredCars = cars.map(car => {
      let scores = {
        ergonomics: 100,
        safety: 100,
        weight: 100,
        environment: 100
      };
      let warnings = [];
      let details = [];

      // 1. PASSENGER CAPACITY
      let maxCapacity = 5;
      const modelLower = car.model.toLowerCase();
      if (car.category === "Picape" && (modelLower.includes("cabine simples") || modelLower.includes("c.s.") || modelLower.includes("cs "))) {
        maxCapacity = 2;
      } else if (car.category === "Esportivo" && (modelLower.includes("roadster") || modelLower.includes("spider") || modelLower.includes("porsche boxster"))) {
        maxCapacity = 2;
      } else if (car.category === "SUV" && (modelLower.includes("7lug") || modelLower.includes("7 lugares") || modelLower.includes("commander") || modelLower.includes("tiggo 8") || modelLower.includes("xc90"))) {
        maxCapacity = 7;
      }

      if (passengers <= maxCapacity) {
        scores.ergonomics = 100;
        details.push(`Capacidade adequada: O carro comporta até ${maxCapacity} ocupantes.`);
      } else {
        scores.ergonomics = 20;
        warnings.push(`Espaço insuficiente para passageiros (máx: ${maxCapacity} pessoas).`);
      }

      // 2. TRUNK VOLUME
      const trunkDelta = car.seat_height_mm - trunk;
      if (trunkDelta >= 0) {
        scores.ergonomics = (scores.ergonomics + 100) / 2;
        details.push(`Porta-malas excelente: Oferece ${car.seat_height_mm}L de espaço.`);
      } else if (trunkDelta >= -100) {
        scores.ergonomics = (scores.ergonomics + 75) / 2;
        details.push(`Porta-malas moderado: Um pouco menor que o desejado (${car.seat_height_mm}L).`);
      } else {
        scores.ergonomics = (scores.ergonomics + 35) / 2;
        warnings.push(`Porta-malas pequeno: Faltam ${Math.abs(trunkDelta)}L de espaço.`);
      }

      // 3. FUEL / ECONOMY PILLAR
      if (preferEconomical) {
        if (car.category === "Eletrico" || car.category === "Hatchback") {
          scores.weight = 100;
          details.push("Excelente economia: Modelo leve, compacto ou elétrico altamente eficiente.");
        } else if (car.category === "SUV" || car.category === "Picape") {
          scores.weight = 50;
          warnings.push("Consumo elevado: Utilitários e picapes grandes demandam mais combustível.");
        } else {
          scores.weight = 80;
          details.push("Consumo moderado: Padrão adequado para uso misto.");
        }
      } else {
        scores.weight = 100;
      }

      // 4. PROPULSION MATCHING
      const brandLower = car.brand.toLowerCase();
      if (propulsion === "intermediate") {
        // Hibrido / Eletrico
        const isEco = (car.category === "Eletrico" || modelLower.includes("hybrid") || modelLower.includes("híbrid") || modelLower.includes("hev") || modelLower.includes("phev") || modelLower.includes("recharge") || brandLower === "byd" || brandLower === "gwm");
        if (isEco) {
          scores.safety = 100;
          details.push("Motorização sustentável: Modelo elétrico/híbrido eficiente.");
        } else {
          scores.safety = 50;
          warnings.push("Combustão convencional: Não possui suporte elétrico/híbrido.");
        }
      } else if (propulsion === "expert") {
        // Diesel
        const isDiesel = (modelLower.includes("diesel") || modelLower.includes("tdi") || modelLower.includes(" 4x4 d") || modelLower.includes("turbo d"));
        if (isDiesel || (car.category === "Picape" && car.power_hp >= 160)) {
          scores.safety = 100;
          details.push("Motorização diesel: Alto torque e grande autonomia rodoviária.");
        } else {
          scores.safety = 40;
          warnings.push("Combustível flex/gasolina: Modelo não oferece motorização diesel.");
        }
      } else {
        // Flex / Gasoline (beginner)
        const isConv = (!modelLower.includes("diesel") && car.category !== "Eletrico");
        if (isConv) {
          scores.safety = 100;
          details.push("Motorização flex/gasolina: Custo de manutenção simples e fácil abastecimento.");
        } else {
          scores.safety = 70;
          warnings.push("Motorização alternativa: Modelo diesel ou elétrico fora do perfil convencional.");
        }
      }

      // 5. CÂMBIO AUTOMÁTICO
      if (requireAutomatic) {
        const isAuto = (modelLower.includes("aut") || modelLower.includes("cvt") || car.category === "Eletrico" || brandLower === "byd" || brandLower === "gwm" || brandLower === "volvo");
        if (isAuto) {
          scores.safety = (scores.safety + 100) / 2;
          details.push("Câmbio Automático: Transmissão automática/CVT para maior conforto.");
        } else {
          scores.safety = (scores.safety + 30) / 2;
          warnings.push("Câmbio Manual: Modelo exige troca de marchas mecânica.");
        }
      }

      // 6. ROAD CONDITIONS & LOCATION
      if (roadType === "rough") {
        if (car.category === "SUV" || car.category === "Picape") {
          scores.environment = 100;
          details.push("Excelente para vias ruins: Vão livre elevado minimiza impactos e raspadas.");
        } else {
          scores.environment = 60;
          warnings.push("Vias ruins: Suspensão convencional requer cuidado redobrado.");
        }
      } else {
        scores.environment = 100;
      }

      if (location === "capital") {
        if (car.category === "Picape") {
          scores.environment = (scores.environment + 50) / 2;
          warnings.push("Uso urbano difícil: Dimensões grandes complicam garagens e trânsito.");
        } else if (car.category === "Hatchback" || car.category === "Eletrico") {
          scores.environment = (scores.environment + 100) / 2;
          details.push("Excelente para cidade: Fácil de estacionar e manobrar.");
        }
      }

      // Calculate composite weighted compatibility score
      let compositeScore = Math.round(
        scores.ergonomics * 0.35 +
        scores.safety * 0.25 +
        scores.weight * 0.20 +
        scores.environment * 0.20
      );

      // Budget logic
      let isOverBudget = false;
      if (car.fipe_price_brl > maxBudget) {
        isOverBudget = true;
        if (!strictBudget) {
          compositeScore = Math.max(0, compositeScore - 25);
          const formattedFipe = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(car.fipe_price_brl);
          warnings.push(`Excede o orçamento máximo (FIPE: ${formattedFipe}).`);
        }
      }

      // Clamp score
      compositeScore = Math.max(0, Math.min(100, compositeScore));

      return {
        bike: car,
        score: compositeScore,
        warnings,
        details,
        isOverBudget
      };
    });

    if (strictBudget) {
      scoredCars = scoredCars.filter(item => !item.isOverBudget);
    }

    scoredCars.sort((a, b) => b.score - a.score);
    renderResults(scoredCars);
  }

  function renderResults(scoredCars) {
    const resultsList = document.getElementById("results-list");
    resultsList.innerHTML = "";

    scoredCars.forEach(item => {
      const car = item.bike;
      const score = item.score;
      
      const card = document.createElement("div");
      card.className = "result-card";
      
      let badgeStyle = "color: var(--accent-success);";
      if (score < 50) {
        badgeStyle = "color: #ff4a86; border-color: rgba(254, 0, 114, 0.3);";
      } else if (score < 80) {
        badgeStyle = "color: #ffb700; border-color: rgba(255, 183, 0, 0.3);";
      }

      const formattedPrice = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        maximumFractionDigits: 0
      }).format(car.fipe_price_brl);

      let headerHTML = `
        <div class="result-card-header">
          <div>
            <div class="bike-brand">${car.brand}</div>
            <div class="bike-model">
              ${car.model}
              <small style="font-size: 0.85rem; color: #a1a9bb; font-weight: normal; margin-left: 5px;">
                (${car.is_used ? car.year : 'Zero Km'})
              </small>
            </div>
          </div>
          <span class="match-percentage-badge" style="${badgeStyle}">${score}% Match</span>
        </div>
      `;

      let specsHTML = `
        <div class="specs-row">
          <div class="spec-block">
            <div class="spec-block-val">${car.seat_height_mm} L</div>
            <div class="spec-block-lbl">Porta-Malas</div>
          </div>
          <div class="spec-block">
            <div class="spec-block-val">${car.wet_weight_kg} kg</div>
            <div class="spec-block-lbl">Peso</div>
          </div>
          <div class="spec-block">
            <div class="spec-block-val">${car.power_hp} cv</div>
            <div class="spec-block-lbl">Potência</div>
          </div>
        </div>
      `;

      let alertsHTML = "";
      if (item.warnings.length > 0) {
        alertsHTML = `
          <div class="card-verdict-alert warning">
            <strong>Pontos de Atenção:</strong><br>
            ${item.warnings.map(w => `• ${w}`).join("<br>")}
          </div>
        `;
      } else {
        alertsHTML = `
          <div class="card-verdict-alert perfect">
            ✓ Encaixe excelente com o seu perfil de uso!
          </div>
        `;
      }

      let detailsHTML = `
        <ul class="suitability-details">
          ${item.details.map(d => `<li><span class="bullet-ok">✓</span> ${d}</li>`).join("")}
        </ul>
      `;

      let bodyHTML = `
        <div class="result-card-body">
          ${specsHTML}
          ${alertsHTML}
          ${detailsHTML}
          <div class="price-box">
            <span class="price-label">Média FIPE:</span>
            <span class="price-value">${formattedPrice}</span>
          </div>
        </div>
      `;

      card.innerHTML = headerHTML + bodyHTML;
      resultsList.appendChild(card);
    });

    document.querySelector(".quiz-card").classList.add("hidden");
    resultsWrapper.classList.remove("hidden");
    resultsWrapper.scrollIntoView({ behavior: "smooth" });
  }
});
