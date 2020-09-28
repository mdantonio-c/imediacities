import { Injectable } from "@angular/core";
import { FormlyFieldConfig } from "@ngx-formly/core";
import { BaseProjectOptions } from "@rapydo/base.project.options";

@Injectable()
export class ProjectOptions extends BaseProjectOptions {
  private terms_of_use: string;
  private privacy_policy: string;
  private research_declaration: string;

  constructor() {
    super();
    this.initTemplates();
  }

  show_groups(): boolean {
    return true;
  }

  custom_user_data(): any[] {
    return [
      { name: "Institution", prop: "declared_institution", flexGrow: 0.7 },
    ];
  }

  privacy_statements() {
    return [
      { label: "Terms of Use", text: this.terms_of_use },
      { label: "Privacy Policy", text: this.privacy_policy },
      { label: "Research declaration", text: this.research_declaration },
    ];
  }

  cookie_law_text(): string {
    // return null to enable default text
    return null;
  }

  cookie_law_button(): string {
    // return null to enable default text
    return null;
  }

  registration_disclaimer(): string {
    return `
Welcome to the registration page of I-Media-Cities. Registering a personal account is free of charge, in compliance with European law, and will allow you to enjoy a whole list of additional platform functionalities, such as adding your own information to films and photographs.<br>
<br>
<strong>In order to explore the I Media Cities platform you have to register yourself with a valid e-mail address. We will send you a confirmation link after the registration.</strong>
`;
  }

  custom_registration_options(): FormlyFieldConfig[] {
    let fields: FormlyFieldConfig[] = [];

    fields.push({
      key: "declared_institution",
      type: "select",
      templateOptions: {
        label: "Do you work at one of the following institutions:",
        required: true,
        addonLeft: {
          class: "fa fa-university",
        },
        options: [
          { label: "Archive", value: "archive" },
          { label: "University", value: "university" },
          { label: "Research Institution", value: "research_institution" },
          { label: "None of the above", value: "none" },
        ],
      },
    });

    return fields;
  }

  private initTemplates() {
    this.terms_of_use = `
<p>
    <br/>
    Please read these Terms of Use,
    <u>
        <a href="http://imc-public.hpc.cineca.it/IMC/privacy-policy/">
            the Privacy Policy
        </a>
    </u>
    and
    <u>
        <a href="http://imc-public.hpc.cineca.it/IMC/disclaimer/">
            the Disclaimer
        </a>
    </u>
    carefully, before starting to use any of the I-Media-Cities web services.
</p>
<p>
    <u></u>
</p>
<p>
    <u>Introduction</u>
</p>
<p>
    Welcome to <strong>I-Media-Cities</strong>. These are the general terms and
    conditions on which we supply all our services. If you use our services,
    you agree to abide by these terms.
</p>
<p>
    At I-Media-Cities we supply a lot of different services. Some of them will
    have specific terms tailored for them. If that is the case, I-Media-Cities’
    contract with you for that service will be on these terms, supplemented by
    any terms specific to the service. In the case of any conflict, service
    specific terms will take precedence.
</p>
<p>
    We process personal data in accordance with the
    <u>
        <a
            href="http://webcache.googleusercontent.com/search?q=cache:pSuT8X4Q5MAJ:ec.europa.eu/research/participants/data/ref/h2020/grants_manual/hi/oa_pilot/h2020-hi-oa-pilot-guide_en.pdf+&amp;cd=1&amp;hl=en&amp;ct=clnk&amp;gl=be"
        >
            Open access to research data policy of the European Union
        </a>
    </u>
    and the
    <u>
        <a href="https://www.eugdpr.org/">
            EU General data Protection Regulation (GDPR).
        </a>
    </u>
    As part of this agreement you consent to our doing so. You should read the
    privacy policy carefully, especially if you have any concerns about your
    privacy.
</p>
<p>
    <strong>
        Warning: unless we have agreed a particular level of service with you,
        we make absolutely no promises about the quality or existence of any of
        our services. Please read the sections below and our general exclusion
        of liability.
    </strong>
</p>
<p>
    All use of our web services are subject to our terms for web users (See
    point 2 below). In point 4 below you can also find some general terms and
    definitions.
</p>
<p>
    <u></u>
</p>
<p>
    <u>Terms of Use for our web services</u>
</p>
<p>
    Web services include any of our websites.
</p>
<p>
    <strong>A. What you agree to</strong>
</p>
<p>
    You agree not to use our websites to do any of the following:
</p>
<p>
    · Anything which is illegal either where you are in the world, or where we
    are.
</p>
<p>
    · Please refrain from the use of any inappropriate or hurtful language.
    I-Media-Cities in no way condones racism or any other form of prejudice.
    Please remember that anything you write on the internet can and will be
    found and read by several different people. I-Media-Cities will remove any
    hurtful or inappropriate comments and contributions and might deny
    offenders access to any part of their web services.
</p>
<p>
    · Try to remember that not everyone has the same opinion as you might have.
    Not everybody considers history in the same way. If something is not clear,
    always ask for clarification first.
</p>
<p>
    · Cause nuisance to other users of our services
</p>
<p>
    · Interfere with the normal running of our services
</p>
<p>
    · Try to access our systems in a way other than those advertised by us and,
    in particular, to extract or download content from our platform. For more
    information on this, see item B of these terms, for more information.
</p>
<p>
    · I-Media-Cities retains the right to judge, edit or remove any
    contribution and comments from its users and visitors. If any of these
    contributions are considered to be inappropriate by I-Media-Cities, they
    will be edited or removed without I-Media-Cities having to give formal
    notice of this change.
</p>
<p>
    · If you consider any of the contributions or comments on any of the web
    services of I-Media-Cities to be inappropriate or hurtful, please don’t
    hesitate to contact us via
    <u>
        <a href="mailto:I-Media-Cities@cinematek.be">
            I-Media-Cities@cinematek.be
        </a>
    </u>
    .
</p>
<p>
    · I-Media-Cities wants to hear from you. Please submit all your questions,
    comments and or recommendations via
    <u>
        <a href="mailto:I-Media-Cities@cinematek.be">
            I-Media-Cities@cinematek.be
        </a>
    </u>
    .
</p>
<p>
    <strong>B. Inappropriate use of the I-Media-Cities web services</strong>
</p>
<p>
    · You agree not to distribute any part of or parts of the Website or the
    Service, including but not limited to any Content, in any medium without
    I-Media-Cities’ prior written authorization, unless I-Media-Cities makes
    available the means for such distribution through functionalities offered
    by the platform.
</p>
<p>
    · You agree not to access Content through any technology or means other
    than the pages of the Website itself, the content players, or such other
    means as I-Media-Cities may explicitly designate for this purpose;
</p>
<p>
    · You agree not to (or attempt to) circumvent, disable or otherwise
    interfere with any security related features of the platform or features
    that (i) prevent or restrict use or copying of Content or (ii) enforce
    limitations on use of the platform or the content accessible via the
    platform.
</p>
<p>
    · You agree not to access Content for any reason other than your personal,
    non-commercial use solely as intended through and permitted by the normal
    functionality of the platform, and solely for Streaming. “Streaming” means
    a contemporaneous digital transmission of the material by I-Media-Cities
    via the Internet to a user operated Internet enabled device in such a
    manner that the data is intended for real-time viewing and not intended to
    be downloaded (either permanently or temporarily), copied, stored, or
    redistributed by the user.
</p>
<p>
    · You shall not copy, reproduce, distribute, transmit, broadcast, display,
    sell, license, or otherwise exploit any Content for any other purposes
    without the prior written consent of I-Media-Cities or the respective
    licensors of the Content.
</p>
<p>
    · You agree not to use or launch any automated system (including, without
    limitation, any robot, spider or offline reader) that accesses the Service
    in a manner that sends more request messages to the YouTube servers in a
    given period of time than a human can reasonably produce in the same period
    by using a publicly available, standard (i.e. not modified) web browser.
</p>
<p>
    · It is not permitted to use any information on our web services to extract
    and collect any user’s personal data or any other kind of user information.
</p>
<p>
    · Without our express consent, it is not permitted to use any part of our
    web services to contact any of our users with commercial or other types of
    messages and comments.
</p>
<p>
    · It is not permitted to use any part of any of our web services to
    distribute any messages of a commercial or idealistic nature. It is a given
    that this is also not permitted by distributing them as a contribution or
    comment.
</p>
<p>
    <strong>C. Other websites</strong>
</p>
<p>
    Some of our activities are carried out on web platforms provided by third
    parties. For example the geolocation tagging is hosted on Google. If you
    make use of any service where that is the case, you are responsible for
    complying with any terms of service of the third party platform.
</p>
<p>
    The web services of I-Media-Cities might contain hyperlinks to third party
    websites. I-Media-Cities has no claims nor control over these third party
    websites and the user has to comply to any and all terms of service
    applicable to this third party platform. I-Media-Cities cannot be held
    accountable or liable for any damages that might derive from the use of
    these third party websites and platforms.
</p>
<p>
    <strong>D. Accounts</strong>
</p>
<p>
    Some of our services require you to create an account in order to make
    certain, or any, use of the service. Your personal profile consists of at
    least your user name and an email address.
</p>
<p>
    By logging in to your user account, you are able to contribute to certain
    parts of our web services. Your activities will be linked to your personal
    account. You are allowed to remove anything you have added to any part of
    our web services. Please also carefully check the Privacy Policy of
    I-Media-Cities.
</p>
<p>
    Your profile is protected by a password, which you yourself have chosen.
    Please keep this password private and never share it with anyone else.
    Change your password regularly.
</p>
<p>
    All our accounts are subject to the following rules.
</p>
<p align="center">
    <em>Rules for our accounts</em>
</p>
<p>
    · You must be at least 18 years old and a human being.
</p>
<p>
    · If asked for any personal details, you must answer truthfully (see our
    privacy policy for what we do with those details). You must supply us with
    a valid e-mail address.
</p>
<p>
    · You are responsible for the security of your accounts and making sure
    that any contact details in the account are kept up to date. If we need to
    contact you but are unable to do so, for example because your e-mail
    address is no longer valid, then any consequences of that failure will be
    your responsibility.
</p>
<p>
    · You must not let anyone else use your account. If pressure is applied to
    you to do so — for example if an employer demands your username and
    password — please inform them that their attempt to subvert your agreement
    with us will mean that they have no permission to use any of our services.
    We may take action, including criminal prosecution, if they use our
    services using an account they have obtained in this way.
</p>
<p>
    · You must let us know of any un-authorized use of your account as soon as
    you are able to after becoming aware of it. Please contact us via
    <u>
        <a href="mailto:I-Media-Cities@cinematek.be">
            I-Media-Cities@cinematek.be
        </a>
    </u>
</p>
<p>
    · Unless an account is associated with a paid-for service, we may suspend
    or terminate it at any time. Equally, you may close your account at any
    time
</p>
<p align="center">
    <em>Removal of your accounts</em>
</p>
<p>
    You can ask to review all information contained in your user profile or
    even to have your user profile removed at any given time. In order to do
    so, please send a message with your request to
    <u>
        <a href="mailto:I-Media-Cities@cinematek.be">
            I-Media-Cities@cinematek.be
        </a>
    </u>
    . In case of an account removal, I-Media-Cities retains the right not to
    remove parts of or entire contributions attached to that account, if
    I-Media-Cities judges these contributions to be of general use to the web
    services. If that is the case, I-Media-Cities will take over the copyright
    and responsibility of these contributions. If expressly asked,
    I-Media-Cities will also change the user name and source attached. The
    I-Media-Cities Consortium will reply within four weeks of them receiving
    your request whether and to what extent your request will be fulfilled.
</p>
<p>
    <strong>E. Community Members</strong>
</p>
<p>
    Our most important class of account is one you may create in order to
    become a community member. By registering as a community member, you are
    acknowledging your connection to us. You are subject to any rules for
    community members we may publish and we may send you email messages we
    think appropriate for members, for example in order to poll you on some
    important issue.
</p>
<p>
    Community membership is not membership in the formal sense of membership of
    a company limited by guarantee.
</p>
<p>
    <strong>F. Content and intellectual property</strong>
</p>
<p align="center">
    <em>General Rules</em>
</p>
<p>
    · Users of our web services with a personal account, can contribute to
    specific parts of our web services.
</p>
<p>
    · Contributions you provide to any part of the web services can be indexed
    and tagged, which will allow them to be linked to other contributions on
    and parts of the web services.
</p>
<p>
    · Contributions and comments are public and visible for all users and
    visitors of the I-Media-Cities web services. You are always responsible for
    the content of your own contributions and comments.
</p>
<p align="center">
    <em>Intellectual Property</em>
</p>
<p>
    · When you provide any contribution, you guarantee that you are licensed to
    provide this contribution or comment and that you do not infringe on the
    intellectual property of any third party. You are at all times obligated to
    provide a correct mention of sources and rights holders, if applicable to
    your contributions.
</p>
<p>
    · I-Media-Cities retains the right to edit or remove any contributions and
    comments any of its users or visitors have made on any part of its web
    services, if these contributions or comments are not in line with our terms
    of use or constitute an infringement of any of our terms of use or data
    policies.
</p>
<p>
    · If I-Media-Cities is approached by a third party because of a copyright
    infringement as a result of one or more of your contributions or comments
    on one of our web services, you will be hold accountable for any costs,
    claims and damages I-Media-Cities might encounter as a result.
    I-Media-Cities will do its utmost to limit these claims and costs.
    I-Media-Cities will immediately edit or remove any of its users’ or
    visitors’ contributions that have been reported on as copyright
    infringement.
</p>
<p>
    · User or visitors that repeatedly infringe on our terms of use or any of
    our policies and/or licenses, will be permanently or temporarily refused
    access to any part of our web services.
</p>
<p>
    · Except in cases where a third party has any copyright claims on any part
    of your contributions or comments, you are considered to be the copyright
    holder of any comment and contribution you make on any part of our web
    services. If you feel that you are the copyright holder of any contribution
    or comment anybody else has provided to the I-Media-Cities services, please
    contact us immediately via
    <u>
        <a href="mailto:I-Media-Cities@cinematek.be">
            I-Media-Cities@cinematek.be
        </a>
    </u>
</p>
<p>
    · I-Media-Cities is and wants to be an open source of information.
    Information available on our web services must be able to be shared and
    re-used by third party websites and for educational purposes.
    I-Media-Cities will do its utmost to provide a possibility to share
    information through other channels, such as Github.
</p>
<p align="center">
    <em>What we do with your content</em>
</p>
<p>
    If you contribute content to any of our services, for example by commenting
    on a task, or uploading data, then as a general rule you agree to license
    that content to us under the same license as prevails for that service or
    website.
</p>
<p>
    The only exception to this policy is where a service we supply to you
    expressly allows a different license, for example a task run submitted to a
    given project would contain your data under whatever license — including no
    license — you choose.
</p>
<p>
    <strong>G. Our content</strong>
</p>
<p>
    Unless otherwise stated all our services and content are offered under open
    data licenses and you should refer to the provisions of the license in
    question to find out what you are allowed to do. Some of our data belongs
    to third parties. Most third party data is subject to an open license, but
    we cannot guarantee it. You should refer to the third party if you are in
    doubt.
</p>
<p>
    The contact information of the specific party that can help you with any
    questions on ownership of the content is clearly listed with every specific
    content item on the I-Media-Cities website.
</p>
<p>
    You are obliged to always mention I-Media-Cities when referencing any part
    of us under license and provide a link to the correct part of our web
    services.
</p>
<p>
    All parts of the brand, the trademarks and the logos of I-Media-Cities are
    protected under copyright law and can in no way be licensed or reused by
    unauthorized parties.
</p>
<p>
    <strong>H. Ownership does not change</strong>
</p>
<p>
    As a general rule, this agreement will not change the ownership of any
    intellectual property belonging to either party. Where your content is used
    by us or vice versa both you and we would do so under a license (see
    above).
</p>
<p>
    <strong>I. Liability</strong>
</p>
<p>
    <em>Indemnities where you may owe us</em>
</p>
<p>
    If you breach any of your obligations under this agreement and, as a
    result, cause us to be sued by anyone else, you will have to compensate us
    for any loss we have suffered as a result, which includes any costs, such
    as paying lawyers, or for our own time, we incur defending a claim as well
    as any damages awarded. If your breach causes you to be sued by someone
    else, you will not sue us for any loss you suffer as a result.
</p>
<p>
    Unless clearly expressed otherwise, all contributions by any of our users
    and visitors on any of our web services are the responsibility of our users
    and visitors. In other words, no rights or claims towards I-Media-Cities
    can be attributed to any of contribution or comment made by users or
    visitors on our web services. I-Media-Cities cannot be held accountable for
    any damages that might occur as a result of any contributions or comments
    any user has provided to any part of the I-Media-Cities web services.
</p>
<p>
    <em>Exclusion what we do not owe you</em>
</p>
<p>
    We limit our liability in several different ways – all of which we believe
    to be fair. In case any one of them is found to be unenforceable by a
    court, each of the following limitations of liability is separate and our
    liability to you is limited by all of them.
</p>
<p>
    · All exclusions of liability are only in so far as we are allowed to do so
    by whatever law applies to the situation.
</p>
<p>
    · We will not be liable for any damage that was not reasonably foreseeable
    at the time we made this agreement.
</p>
<p>
    · We are not liable for any loss which is indirect or consequential. That
    includes any loss of business or profit.
</p>
<p>
    · We exclude, in so far as we are allowed, any warranties that would be
    implied by law.
    <br/>
    <br/>
</p>
<p>
    <u>Open Licenses</u>
</p>
<p>
For datasets, we make a distinction between <em>source</em> data and<em>derived</em> data. Our crowd-sourcing projects use digital    <em>source</em> data (for example films, photographs, scanned documents) to
    allow contributors to complete research tasks such as the tagging and
    transcription. This <em>source</em> data will not typically be available
    through a Creative Commons license, as the institutions owning the archival
    material have asked that commercial use is prohibited without further
    consultation.
</p>
<p>
    All the <em>derived</em> data, produced with the help of volunteers via use
    of any of our web services, is licensed under Creative Commons licenses,
    depending on case-by-case agreements with our partners.
</p>
<p>
    Check the project’s information pages for further details about which
    specific licenses have been applied.
</p>
<p>
    <u>General conditions</u>
</p>
<p>
    We may update these terms and conditions at any time. If we do so, we will
announce the change via our main site (    <u><a href="http://www.imediacities.eu/">www.imediacities.eu</a></u>). Any
    changes will be binding on you from the moment we announce them. All terms,
    policies and rules applying to I-Media-Cities will always be accessible and
    available on a dedicated part of the website.
</p>
<p>
    This agreement is made under the laws of Belgium. I-Media-Cities will
    always try to solve any problems and differences of opinion amicably and
    through communication. If all else fails, these differences will be
    referred to a court of law in Belgium.
</p>
<p>
    Boilerplate
</p>
<p>
    These final “boilerplate” terms should go without saying, but we are saying
    them anyway just to be clear.
</p>
<p>
    · If any part of this agreement is ineffective, then the rest of the
    agreement should be read without it.
</p>
<p>
    · This agreement is between you and us and is not intended to give anyone
    else any rights.
</p>
<p>
    · We may sometimes fail to enforce our rights under this agreement (for
    example because we decide not to, or we did not realize you were in breach
    of contract). Just because we have not enforced any of our rights, does not
    stop us from doing so in the future.
</p>
<p>
    · Neither party is liable for anything which is beyond their reasonable
    control.
</p>
<p>
    · If for some reason beyond I-Media-Cities’ reasonable control, we are
    unable to or it would not be commercially viable for us to, continue to
    supply any of our services, we may cease to supply that service, ending any
    agreement between us for its supply. If we do so, we will return to you a
    fair proportion of any sum you have paid us in advance for the supply of
    that service, taking into account the service we have already supplied to
    you.
</p>
<p>
    Further Information
</p>
<p>
    I-Media-Cities and any of its web services are copyright protected and
    controlled by the I-Media-Cities Consortium. Any comments, questions and
    complaints can, at all times, be directed to the address and telephone
    numbers below.
</p>
<p>
    I-Media-Cities Consortium
</p>
<p>
    Cinematek
</p>
<p>
    Rue Ravenstein 3
</p>
<p>
    1000 Brussels
</p>
<p>
    Belgium
</p>
<p>
    Telephone: 0032/2 551 19 00
</p>

        `;
    this.privacy_policy = `
<p>
    Please read this Privacy Policy,
    <u>
        <a href="http://imc-public.hpc.cineca.it/IMC/terms-of-use/">
            the Terms of Use
        </a>
    </u>
    and the
    <u>
        <a href="http://imc-public.hpc.cineca.it/IMC/disclaimer/">
            Disclaimer
        </a>
    </u>
    carefully, before starting to use any of the I-Media-Cities web services.
</p>
<p>
    <strong><u></u></strong>
</p>
<p>
    <strong><u>Privacy Policy</u></strong>
</p>
<p>
    This Privacy Policy is applicable to any use of any part of the web
    services of I-Media-Cities.
</p>
<p>
    <strong>Introduction</strong>
</p>
<p>
    The I-Media-Cities Consortium considers the privacy of and dealing with
    personal data of the users of our web services as extremely important.
    Personal data are carefully and respectfully collected, processed and
    stored, in accordance with all applicable national, European and
    international laws.
</p>
<p>
    <strong></strong>
</p>
<p>
    <strong>1. Collecting and Processing Personal Data</strong>
</p>
<p>
    The I-Media-Cities Consortium processes personal data of every user who
    registers an account on the website, provides a contribution or comment to
    any part of our web services, or register to receive a newsletter. In order
    to be able to provide a contribution or comment, a user is required to at
    least register a user name and an email address. In order to receive a
    newsletter, a user has to at least register an email address.
</p>
<p>
    If you register an account at I-Media-Cities, you are able to provide the
    platform with added information. It is your decision and responsibility
    which added information you provide to the I-Media-Cities web service. Some
    or all of your activities on any of the I-Media-Cities web services will be
    added to your personal workspace.
</p>
<p>
    Your comments and contributions can also be shared on third party sites and
    web solutions, such as Facebook, Twitter, etc. Because of the general
    functionalities of the internet, public contributions will be registered by
    websites such as Google.
</p>
<p>
    <strong></strong>
</p>
<p>
    <strong>2. Purpose of Processing Personal Data</strong>
</p>
<p>
    The I-Media-Cities Consortium collects and processes your data in order to
    optimize, adjust, enhance and develop our web services and their usability.
</p>
<p>
    The I-Media-Consortium can also use your data to offer and suggest relevant
    information, but will never provide third parties access to any of your
    data or sell your data for any purpose.
</p>
<p>
    Other than the way it was written in this Privacy Policy and restricted to
    the rules and regulations of all applicable laws, I-Media-Cities will not
    make any of your personal data public, unless: (a) it is obligated to on
    the grounds of law, regulations, orders of conduct or ordered to by a court
    ruling; (b) it is necessary for the sake of security reasons; and/or (c)
    the I-Media-Cities Consortium has a reasonable suspicion the relevant user
    is part of any illegal activities.
</p>
<p>
    <strong></strong>
</p>
<p>
    <strong>3. Cookies</strong>
</p>
<p>
    Every time a user visits the website, that visit will be registered by
    means of so-called ‘cookies’. Cookies are small files that are stored on
    the user’s hard drive, which allow the I-Media-Cities Consortium to access
    information about the use of their website and which allows for
    preferences, user names and passwords to be automatically remembered. This
    information can also be analyzed to discover trends and draw statistics
    relating to such things as the parts of the website that are most visited,
    average time of a visit, etc. In order to do this, I-Media-Cities will use
    Google Analytics (on which the
    <u>
        <a href="https://www.google.com/policies/privacy/">
            privacy policy of Google
        </a>
    </u>
    applies)
</p>
<p>
    The information that is collected through cookies can only be coupled to a
    computer and not to a specific user. It will therefore not allow the
    I-Media-Cities Consortium to derive any conformation that reveals the
    identity of a user. You have the ability to format your browser in such a
    way that cookies are refused. By doing this, it is possible that the
    website will no longer function optimally.
</p>
<p>
    <strong></strong>
</p>
<p>
    <strong>4. Storage and Safety of Personal Data</strong>
</p>
<p>
    The personal data you provided to register an account on any of our
    services and websites are stored on protected servers at CINECA, Via
    Magnanelli, 6/3, 40033 Casalecchio di Reno BO, Italy. Personal data you
    provided to register for newsletters is stored in protected servers at the
open source newsletter software provider    <a href="http://www.mailchimp.com/">Mailchimp</a>.
</p>
<p>
    The I-Media-Cities Consortium will take every organizational and technical
    measure deemed reasonable to make sure your personal data are safe, correct
    and up-to-date. The I-Media-Cities Consortium will safely store your
    personal account data and take all necessary measures to protect them from
    loss, abuse, illegal access and publication. The Consortium, however,
    cannot guarantee that personal data transferred over the internet are
    always 100% protected.
</p>
<p>
    The I-Media-Cities Consortium will take reasonable measures to remove
    personal data or make them anonymous, as soon as they no longer need to be
    stored.
</p>
<p>
    <strong></strong>
</p>
<p>
    <strong>5. Access to, Correction and Removal of Personal Data</strong>
</p>
<p>
    At any given time, you are able to send the I-Media-Cities Consortium a
    request to receive all personal data they have stored of you. The
    I-Media-Cities Consortium will make sure that the requested information is
    send to you within four weeks of them receiving your request.
</p>
<p>
    <strong>
        If you would like to change, correct or ask to remove your own personal
        data, you can submit a request to do so via
    </strong>
    <strong>
        <u>
            <a href="mailto:I-Media-Cities@cinematek.be">
                I-Media-Cities@cinematek.be
            </a>
        </u>
    </strong>
    <strong>
        . The I-Media-Cities Consortium will reply within four weeks of them
        receiving your request whether and to what extent your request will be
        fulfilled.
    </strong>
</p>
        `;
    this.research_declaration = `
By accepting this research declaration, you agree to the following:
<ul>
    <li> You agree to only use the I-Media-Cities platform and functionalities to
    perform research on the Content.


    <li> You are obliged to always mention I-Media-Cities when referencing any
    part of our platform or any Content present on the platform in any of your
    research related publications, including a link to the correct part of our
    web services or Content.

    <li> You agree not to access Content for any reason other than your personal,
    non-commercial use solely as intended through and permitted by the normal
    functionality of the platform, and solely for Streaming. “Streaming” means
    a contemporaneous digital transmission of the material by I-Media-Cities
    via the Internet to a user operated Internet enabled device in such a
    manner that the data is intended for real-time viewing and not intended to
    be downloaded (either permanently or temporarily), copied, stored, or
    redistributed by the user.

    <li> You shall not copy, reproduce, distribute, transmit, broadcast, display,
    sell, license, or otherwise exploit any Content for any other purposes
    without the prior written consent of I-Media-Cities or the respective
    licensors of the Content.
</ul>
        `;
  }
}
