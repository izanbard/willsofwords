<script setup lang="ts">
import TextBlock from '@/components/TextBlock.vue'
import HeadingBlock from '@/components/HeadingBlock.vue'
import DividerLine from '@/components/DividerLine.vue'
</script>

<template>
  <div class="card">
    <HeadingBlock :level="1">About</HeadingBlock>
    <DividerLine />
    <HeadingBlock :level="2">Introduction</HeadingBlock>
    <TextBlock
      >Wills of Words is a family-founded publishing house where traditional curiosity meets modern
      innovation. Created by a partnership of two brothers—a dedicated researcher and a specialised
      technologist—our mission is to rescue the puzzle world from generic, uninspired content.
    </TextBlock>
    <TextBlock>
      We do not believe in "one size fits all". Every Wills of Words book is born from rigorous,
      data-driven market analysis to identify the high-interest, niche topics that readers truly
      care about. From historical deep-dives to untapped hobbies and specialised interests, we build
      collections that inform as much as they entertain
    </TextBlock>
    <DividerLine />
    <HeadingBlock :level="2">The "Iron-Clad" Quality Standard</HeadingBlock>
    <TextBlock
      >While our lead technologist, Izzy, utilises bespoke, proprietary software to ensure our grids
      are perfectly constructed and dynamically structured, we never leave the final product to the
      machines. Every word list is hand-vetted for accuracy and every layout is reviewed by Roger to
      ensure a premium large print experience that is easy on the eyes and challenging for the
      brain.
    </TextBlock>
    <TextBlock
      >By choosing Wills of Words, you are choosing the "Roger & Izzy Promise": the perfect harmony
      of sophisticated technology and dedicated human oversight. We guarantee no nonsensical
      word-dumps—only high-quality, vetted content designed for those who value authenticity and the
      thrill of a well-crafted challenge.
    </TextBlock>
    <TextBlock
      >Whether you are looking for cognitive health exercises for seniors, a unique hobby-themed
      activity, or a specialised interest collection, Wills of Words provides precision-crafted
      mental adventures.
    </TextBlock>
    <div class="container">
      <div class="item">
        <img alt="Roger" src="/images/roger.jpg" class="portrait" />
        <HeadingBlock :level="3">Roger</HeadingBlock>
      </div>
      <div class="item">
        <img alt="Izzy" src="/images/izzy.jpg" class="portrait" />
        <HeadingBlock :level="3">Izzy</HeadingBlock>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  justify-content: space-evenly;
  align-items: center;
}
.item {
  align-self: center;
  text-align: center;
}
.portrait {
  width: 250px;
  border-radius: 50%;
}
</style>
