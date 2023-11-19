In this repo, I intent to explore ideas that I got from listening to talks by
[Alan Kay](http://rickardlindberg.me/writing/alan-kay-notes/) and digging into
sources that he references.

He is a tremendous source of inspiration to me, so understanding his ideas
better I think is worthwhile.

## Ideas

### Real OOP

Kay has said that the kind of OOP that we do today is not what he had in mind
when he coined the term.

So what did he have in mind?

He has
[said](http://lists.squeakfoundation.org/pipermail/squeak-dev/1998-October/017019.html) that messaging was the big idea.

So how do we program a set of objects that interact with each other by sending
messages?

### Biology

Kay has said that programs should be more like biology and less like gears.
What does he mean by that?

How do cells organize to create a useful whole? How do cells communicate? Are
there messaging protocols? How are they designed?

Kay has said that we made objects too small. Every cell carries its DNA with
it. How does that translate to objects in software? What is the DNA of an
object? Is that what should make them bigger?

Molecules move at random inside cells. If they happen to bump into another
molecule that it matches with, it does. Because the speed is so fast, this
happens often enough. This is similar to how a process matches a message in
tuple-space.

### Message Passing

How do cells talk to each other? Probably not by named messages? They probably
"sense" their surroundings and act accordingly.

One way of "sensing" is with publish-subscribe. If I notify, I don't know (or
care) if someone listens. I send a message without getting a return value.
(Tell, don't ask?) How to design such protocols? How to solve problems without
return values?

### Modern Software Engineering

In his book Modern Software Engineering, Dave Farley gives an example of what
he considers to be good design.

It involves an object notifying subscribers about certain events in it. In that
way, the object can collaborate with other objects without having to know even
who those collaborators are.

### Emerging System Beavhior / Ron Jeffries

In his blog post series about Python game development, Jeffries has used a
design in which simple objects make up a more complex game, and the rules of
the game is not clearly present in code, but emerges from the collaboration
between objects.

### Erlang

Erlang processes are maybe closer to what Kay had in mind for objects. Erlang
processes are isolated from each other and communicated by message passing.

### Linda

A different way of sensing the world is with Linda-like tuple spaces. Messages
are placed in the tuple-space, and if a message matches what you are looking
for, you receive it.

It's a different mental model for how objects collaborate with each other. How
can we design protocols for such collaboration? How to solve problems in this
style?

### Prolog/Requirements

Program in terms of requirements. Put a requirement into tuple space, and
processes will refine the result until you have a worthy solution.

### META II

What is a message? A message can be a stream of bytes, source code, structured
data. You just need to write a parser that understands it.

## My Exploration

The programming environment I intend to explore is a cross between META II,
Linda, and (what I imagine would be) a more appropriate OOP environment.

In [Joe Armstrong & Alan Kay - Joe Armstrong interviews Alan
Kay](https://www.youtube.com/watch?v=fhOHn9TClXY) Kay talks about the
connection between Linda and META II. I also made the connection that a
Linda-like environment could be the base for a more biological, OOP environment
where objects can react based on messages in their surroundings.

* Programs are expressed as information translation machines
* They act like Erlang-style-actors
* The communicate with Linda-style tuple spaces
* Small, independent, pattern-matching machines that solve problems in an
  ensamble-like fashion.
* Eaach machine is super simple. It is easy to test. But how does it create a
  whole? Simulate! Let the computer do the work. How to analyze simulation
  results?

## TODO

* Implement something Actor like
    * An actor has state
    * An actor can spawn new actors
    * Move RLMeta into this style

```
actor Factorial {
    Fact = .:x -> put(["FactIter" x x 0])
               -> spawn(Factorial())
}

actor Main {
}
```
